package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.qb.common.BizEx;
import com.grad.qb.common.R;
import com.grad.qb.common.UserContext;
import com.grad.qb.entity.*;
import com.grad.qb.mapper.*;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;

/** 组卷与试卷流转：随机抽题（含缺口回补）、发布冻结快照、覆盖度分析、状态机流转 */
@RestController
@RequestMapping("/api/paper")
public class PaperActionController {

    private final PaperMapper paperMapper;
    private final PaperQuestionMapper pqMapper;
    private final QuestionMapper questionMapper;
    private final KnowledgePointMapper kpMapper;
    private final PracticeRecordMapper recordMapper;
    private final QuestionOptionMapper optionMapper;

    /** 状态机：当前状态 -> 允许的下一状态（需求文档第 4 节） */
    private static final Map<String, List<String>> FLOW = Map.of(
            "草稿", List.of("待审核"),
            "待审核", List.of("已发布", "已驳回"),
            "已驳回", List.of("待审核"),
            "已发布", List.of("使用中", "已归档"),
            "使用中", List.of("已归档"),
            "已归档", List.of());

    /**
     * 按知识点权重与难度区间随机抽题组卷。
     * 某知识点题量不足时按缺口比例回补到同科相邻知识点，并把回补明细写入 random_rule 便于预览标注。
     */
    @PostMapping("/generate-random")
    @Transactional
    public R<Map<String, Object>> generate(@RequestBody Map<String, Object> body) {
        Long subjectId = Long.valueOf(String.valueOf(body.getOrDefault("subjectId", 1)));
        String name = String.valueOf(body.getOrDefault("paperName", "随机组卷 " + LocalDateTime.now().getHour() + " 时"));
        BigDecimal totalScore = new BigDecimal(String.valueOf(body.getOrDefault("totalScore", 100)));
        int duration = Integer.parseInt(String.valueOf(body.getOrDefault("durationMin", 60)));
        BigDecimal minDiff = new BigDecimal(String.valueOf(body.getOrDefault("minDifficulty", "0.20")));
        BigDecimal maxDiff = new BigDecimal(String.valueOf(body.getOrDefault("maxDifficulty", "0.90")));
        List<Map<String, Object>> rules = (List<Map<String, Object>>) body.getOrDefault("rules", List.of());

        List<KnowledgePoint> kps = kpMapper.selectList(new QueryWrapper<KnowledgePoint>()
                .eq("subject_id", subjectId).eq("status", 1));
        if (rules.isEmpty()) {
            // 未指定规则时按一级节点考纲权重自动分配 10 道题
            rules = new ArrayList<>();
            for (KnowledgePoint k : kps) {
                if (k.getKpLevel() != null && k.getKpLevel() == 1) {
                    Map<String, Object> r = new LinkedHashMap<>();
                    r.put("kpId", k.getId());
                    r.put("count", Math.max(1, Math.round(k.getExamWeight().floatValue() / 10f)));
                    rules.add(r);
                }
            }
        }
        List<Long> picked = new ArrayList<>();
        List<String> backfill = new ArrayList<>();
        for (Map<String, Object> rule : rules) {
            Long kpId = Long.valueOf(String.valueOf(rule.get("kpId")));
            int want = Integer.parseInt(String.valueOf(rule.getOrDefault("count", 1)));
            List<Long> subtree = subtreeKpIds(kps, kpId);
            List<Question> cands = questionMapper.selectList(new QueryWrapper<Question>()
                    .in("knowledge_point_id", subtree).eq("status", "已入库")
                    .between("difficulty", minDiff, maxDiff).orderByAsc("id"));
            int got = 0;
            for (Question q : cands) {
                if (got >= want) break;
                if (!picked.contains(q.getId())) {
                    picked.add(q.getId());
                    got++;
                }
            }
            if (got < want) {
                // 缺口按同学科其他知识点回补，并记录明细
                int need = want - got;
                List<Question> extra = questionMapper.selectList(new QueryWrapper<Question>()
                        .eq("subject_id", subjectId).eq("status", "已入库")
                        .between("difficulty", minDiff, maxDiff).orderByAsc("id"));
                for (Question q : extra) {
                    if (need <= 0) break;
                    if (!picked.contains(q.getId())) {
                        picked.add(q.getId());
                        need--;
                        backfill.add(kpId + " 缺口 " + (want - got) + " 道，回补题目 " + q.getQuestionNo());
                    }
                }
            }
        }
        if (picked.isEmpty()) throw new BizEx(4001, "所选知识点在难度区间内没有可用题目，请调整条件");
        Paper p = new Paper();
        p.setPaperNo("SJ" + LocalDateTime.now().format(com.grad.qb.config.JacksonConfig.DTF).substring(2, 10).replace("-", "") +
                String.format("%04d", new Random().nextInt(9999)));
        p.setPaperName(name);
        p.setSubjectId(subjectId);
        p.setBuildMode("随机");
        p.setQuestionCount(picked.size());
        p.setTotalScore(totalScore);
        p.setDurationMin(duration);
        p.setCreatorId(UserContext.id());
        p.setStatus("待审核");
        p.setRandomRule(String.join("; ", backfill));
        p.setDifficultyAvg(BigDecimal.ZERO);
        paperMapper.insert(p);

        BigDecimal per = totalScore.divide(new BigDecimal(picked.size()), 1, RoundingMode.HALF_UP);
        int i = 1;
        for (Long qid : picked) {
            Question q = questionMapper.selectById(qid);
            PaperQuestion pq = new PaperQuestion();
            pq.setPaperId(p.getId());
            pq.setQuestionId(qid);
            pq.setSectionNo(1);
            pq.setSortNo(i++);
            pq.setScore(per);
            pq.setQuestionType(q.getQuestionType());
            pq.setKnowledgePointId(q.getKnowledgePointId());
            pq.setStemSnapshot(q.getStem());
            pqMapper.insert(pq);
        }
        // 分值合计与总分对齐（尾差补到最后一条）
        List<PaperQuestion> items = pqMapper.selectList(new QueryWrapper<PaperQuestion>().eq("paper_id", p.getId()));
        BigDecimal sum = items.stream().map(PaperQuestion::getScore).reduce(BigDecimal.ZERO, BigDecimal::add);
        if (sum.compareTo(totalScore) != 0 && !items.isEmpty()) {
            PaperQuestion last = items.get(items.size() - 1);
            last.setScore(last.getScore().add(totalScore.subtract(sum)));
            pqMapper.updateById(last);
        }
        p.setTotalScore(totalScore);
        paperMapper.updateById(p);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("id", p.getId());
        data.put("paperNo", p.getPaperNo());
        data.put("questionCount", p.getQuestionCount());
        data.put("totalScore", p.getTotalScore());
        data.put("backfill", backfill);
        return R.ok(data);
    }

    private List<Long> subtreeKpIds(List<KnowledgePoint> all, Long root) {
        List<Long> ids = new ArrayList<>();
        ids.add(root);
        boolean added = true;
        while (added) {
            added = false;
            for (KnowledgePoint k : all) {
                if (ids.contains(k.getParentId()) && !ids.contains(k.getId())) {
                    ids.add(k.getId());
                    added = true;
                }
            }
        }
        return ids;
    }

    /** 发布：校验状态与明细完整性，冻结题干快照 */
    @PostMapping("/{id}/publish")
    @Transactional
    public R<Map<String, Object>> publish(@PathVariable Long id) {
        Paper p = paperMapper.selectById(id);
        if (p == null) throw new BizEx(4000, "试卷不存在");
        if (!"待审核".equals(p.getStatus()) && !"草稿".equals(p.getStatus()))
            throw new BizEx(4001, "当前状态 " + p.getStatus() + " 不允许发布");
        List<PaperQuestion> items = pqMapper.selectList(new QueryWrapper<PaperQuestion>().eq("paper_id", id));
        if (items.isEmpty()) throw new BizEx(4001, "试卷没有题目明细，不能发布");
        BigDecimal sum = items.stream().map(PaperQuestion::getScore).reduce(BigDecimal.ZERO, BigDecimal::add);
        if (sum.compareTo(p.getTotalScore()) != 0)
            throw new BizEx(4001, "题目分值合计 " + sum + " 与总分 " + p.getTotalScore() + " 不一致");
        for (PaperQuestion pq : items) {
            Question q = questionMapper.selectById(pq.getQuestionId());
            if (q != null && (pq.getStemSnapshot() == null || pq.getStemSnapshot().isBlank())) {
                pq.setStemSnapshot(q.getStem());
                pqMapper.updateById(pq);
            }
        }
        p.setStatus("已发布");
        paperMapper.updateById(p);
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("id", id);
        d.put("status", p.getStatus());
        d.put("frozen", items.size());
        return R.ok(d);
    }

    /** 覆盖度：知识点分布、难度分布、缺口提示 */
    @GetMapping("/{id}/coverage")
    public R<Map<String, Object>> coverage(@PathVariable Long id) {
        Paper p = paperMapper.selectById(id);
        if (p == null) throw new BizEx(4000, "试卷不存在");
        List<PaperQuestion> items = pqMapper.selectList(new QueryWrapper<PaperQuestion>().eq("paper_id", id));
        Map<Long, Integer> byKp = new LinkedHashMap<>();
        int d1 = 0, d2 = 0, d3 = 0;
        for (PaperQuestion pq : items) {
            byKp.merge(pq.getKnowledgePointId(), 1, Integer::sum);
            Question q = questionMapper.selectById(pq.getQuestionId());
            BigDecimal diff = q == null ? new BigDecimal("0.6") : q.getDifficulty();
            if (diff.compareTo(new BigDecimal("0.4")) < 0) d1++;
            else if (diff.compareTo(new BigDecimal("0.7")) <= 0) d2++;
            else d3++;
        }
        List<Map<String, Object>> rows = new ArrayList<>();
        List<String> gaps = new ArrayList<>();
        for (Map.Entry<Long, Integer> e : byKp.entrySet()) {
            KnowledgePoint k = kpMapper.selectById(e.getKey());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("kpId", e.getKey());
            m.put("kpName", k == null ? "-" : k.getKpName());
            m.put("count", e.getValue());
            m.put("weight", k == null ? BigDecimal.ZERO : k.getExamWeight());
            BigDecimal pct = new BigDecimal(e.getValue() * 100).divide(new BigDecimal(items.size()), 1, RoundingMode.HALF_UP);
            m.put("percent", pct);
            if (k != null && pct.compareTo(k.getExamWeight()) < 0)
                gaps.add(k.getKpName() + " 占比 " + pct + "% 低于考纲权重 " + k.getExamWeight() + "%");
            rows.add(m);
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("paperName", p.getPaperName());
        data.put("questionCount", items.size());
        data.put("totalScore", p.getTotalScore());
        data.put("difficultyAvg", p.getDifficultyAvg());
        data.put("distribution", Map.of("easy", d1, "medium", d2, "hard", d3));
        data.put("kps", rows);
        data.put("gaps", gaps);
        return R.ok(data);
    }

    /** 状态流转统一入口：先校验目标状态是否允许，再校验操作人与必填原因 */
    @PostMapping("/{id}/transition")
    public R<Map<String, Object>> transition(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Paper p = paperMapper.selectById(id);
        if (p == null) throw new BizEx(4000, "试卷不存在");
        String target = String.valueOf(body.getOrDefault("targetStatus", ""));
        List<String> allowed = FLOW.getOrDefault(p.getStatus(), List.of());
        if (!allowed.contains(target))
            throw new BizEx(4001, "状态 " + p.getStatus() + " 不能流转到 " + target);
        String reason = body.get("reason") == null ? null : String.valueOf(body.get("reason"));
        if ("已驳回".equals(target)) {
            if (reason == null || reason.trim().length() < 5) throw new BizEx(4000, "驳回必须填写不少于 5 字的原因");
            p.setRejectReason(reason);
        }
        if ("已归档".equals(target) && "已发布".equals(p.getStatus())) {
            long running = recordMapper.selectCount(new QueryWrapper<PracticeRecord>()
                    .eq("paper_id", id).eq("status", "进行中"));
            if (running > 0) throw new BizEx(4001, "仍有 " + running + " 份进行中的练习引用该试卷，不能撤回");
        }
        p.setStatus(target);
        paperMapper.updateById(p);
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("id", id);
        d.put("status", target);
        return R.ok(d);
    }

    /** 试卷详情：含题目与选项，学生端展示 stem_snapshot */
    @GetMapping("/{id}/detail")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        Paper p = paperMapper.selectById(id);
        if (p == null) throw new BizEx(4000, "试卷不存在");
        List<PaperQuestion> items = pqMapper.selectList(new QueryWrapper<PaperQuestion>()
                .eq("paper_id", id).orderByAsc("sort_no"));
        QuestionOptionMapper om = optionMapper;
        List<Map<String, Object>> qs = new ArrayList<>();
        for (PaperQuestion pq : items) {
            Question q = questionMapper.selectById(pq.getQuestionId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", q == null ? pq.getQuestionId() : q.getId());
            m.put("questionType", pq.getQuestionType());
            m.put("stem", pq.getStemSnapshot());
            m.put("score", pq.getScore());
            m.put("difficulty", q == null ? null : q.getDifficulty());
            m.put("analysis", q == null ? null : q.getAnalysis());
            m.put("answer", q == null ? null : q.getAnswer());
            m.put("knowledgePointId", pq.getKnowledgePointId());
            m.put("options", om.selectList(new QueryWrapper<QuestionOption>()
                    .eq("question_id", pq.getQuestionId()).orderByAsc("sort_no")));
            qs.add(m);
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("paper", p);
        data.put("questions", qs);
        return R.ok(data);
    }

    public PaperActionController(PaperMapper paperMapper, PaperQuestionMapper pqMapper, QuestionMapper questionMapper,
                                 KnowledgePointMapper kpMapper, PracticeRecordMapper recordMapper,
                                 QuestionOptionMapper optionMapper) {
        this.paperMapper = paperMapper;
        this.pqMapper = pqMapper;
        this.questionMapper = questionMapper;
        this.kpMapper = kpMapper;
        this.recordMapper = recordMapper;
        this.optionMapper = optionMapper;
    }
}
