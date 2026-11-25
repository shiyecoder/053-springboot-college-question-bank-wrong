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
import java.time.LocalDateTime;
import java.util.*;

/** 题目审核（不得审自己的题）、批量导入（逐行校验）、题目详情、知识点树与权重批量调整 */
@RestController
@RequestMapping("/api")
public class QuestionActionController {

    private final QuestionMapper questionMapper;
    private final QuestionOptionMapper optionMapper;
    private final QuestionAuditMapper auditMapper;
    private final KnowledgePointMapper kpMapper;
    private final ImportTaskMapper importMapper;
    private final SysMessageMapper messageMapper;
    private final SysOperLogMapper logMapper;
    private final SubjectMapper subjectMapper;

    public QuestionActionController(QuestionMapper questionMapper, QuestionOptionMapper optionMapper,
                                    QuestionAuditMapper auditMapper, KnowledgePointMapper kpMapper,
                                    ImportTaskMapper importMapper, SysMessageMapper messageMapper,
                                    SysOperLogMapper logMapper, SubjectMapper subjectMapper) {
        this.questionMapper = questionMapper;
        this.optionMapper = optionMapper;
        this.auditMapper = auditMapper;
        this.kpMapper = kpMapper;
        this.importMapper = importMapper;
        this.messageMapper = messageMapper;
        this.logMapper = logMapper;
        this.subjectMapper = subjectMapper;
    }

    /** 题干相似度校验：与同学科已有题目比对，命中 85% 以上时返回最相似的一条 */
    @GetMapping("/question/similar")
    public R<Map<String, Object>> similar(@RequestParam String stem,
                                          @RequestParam(required = false) Long subjectId,
                                          @RequestParam(required = false) Long excludeId) {
        String target = normalize(stem);
        Map<String, Object> best = null;
        double bestRate = 0;
        QueryWrapper<Question> w = new QueryWrapper<Question>().ne("deleted", 1);
        if (subjectId != null) w.eq("subject_id", subjectId);
        if (excludeId != null) w.ne("id", excludeId);
        for (Question q : questionMapper.selectList(w)) {
            if (q.getStem() == null) continue;
            double rate = similarity(target, normalize(q.getStem()));
            if (rate > bestRate) {
                bestRate = rate;
                best = new LinkedHashMap<>();
                best.put("id", q.getId());
                best.put("questionNo", q.getQuestionNo());
                best.put("stem", q.getStem());
                best.put("status", q.getStatus());
            }
        }
        if (best == null) return R.ok(Map.of("rate", 0));
        best.put("rate", BigDecimal.valueOf(bestRate).setScale(1, java.math.RoundingMode.HALF_UP));
        return R.ok(best);
    }

    /** 记录强制入库的差异说明，便于事后追溯重复题判断依据 */
    @PostMapping("/question/{id}/diff-note")
    public R<Void> diffNote(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        String note = String.valueOf(body.getOrDefault("note", "")).trim();
        if (note.length() < 5) throw new BizEx(4002, "差异说明不少于 5 字");
        Question q = questionMapper.selectById(id);
        if (q == null) throw new BizEx(4000, "题目不存在");
        SysOperLog log = new SysOperLog();
        log.setOperId(UserContext.id());
        log.setOperName(UserContext.name());
        log.setModule("题库管理");
        log.setOperType("重复题强制入库");
        log.setBizNo(q.getQuestionNo());
        log.setContent("题干相似度超阈值，差异说明：" + note);
        log.setOperTime(LocalDateTime.now());
        logMapper.insert(log);
        return R.ok(null);
    }

    /** 归一化：去空白与标点，只保留文字与数字，避免排版差异影响相似度 */
    private String normalize(String s) {
        return s == null ? "" : s.replaceAll("[\\s\\p{Punct}，。、；：？！“”‘’（）《》【】]", "");
    }

    /** 相似度：最长公共子序列长度 / 较长文本长度，取值 0-100 */
    private double similarity(String a, String b) {
        if (a.isEmpty() || b.isEmpty()) return 0;
        int n = a.length(), m = b.length();
        int[] prev = new int[m + 1];
        int[] cur = new int[m + 1];
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                cur[j] = a.charAt(i - 1) == b.charAt(j - 1)
                        ? prev[j - 1] + 1
                        : Math.max(prev[j], cur[j - 1]);
            }
            int[] t = prev; prev = cur; cur = t;
            Arrays.fill(cur, 0);
        }
        return prev[m] * 100.0 / Math.max(n, m);
    }

    /** 题库列表配图索引：返回 questionId -> 首个选项配图，用于列表缩略图 */
    @GetMapping("/question/figure-index")
    public R<Map<Long, String>> figureIndex() {
        Map<Long, String> map = new LinkedHashMap<>();
        for (QuestionOption o : optionMapper.selectList(new QueryWrapper<QuestionOption>()
                .isNotNull("image_url").ne("image_url", "").orderByAsc("sort_no"))) {
            map.putIfAbsent(o.getQuestionId(), o.getImageUrl());
        }
        return R.ok(map);
    }

    /** 题目详情：含选项、审核流水 */
    @GetMapping("/question/{id}/detail")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        Question q = questionMapper.selectById(id);
        if (q == null) throw new BizEx(4000, "题目不存在");
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("question", q);
        d.put("options", optionMapper.selectList(new QueryWrapper<QuestionOption>()
                .eq("question_id", id).orderByAsc("sort_no")));
        d.put("audits", auditMapper.selectList(new QueryWrapper<QuestionAudit>()
                .eq("question_id", id).orderByDesc("audit_time")));
        return R.ok(d);
    }

    /** 审核：通过入库 / 退回；审核人不得为创建人，退回必须选原因并填说明 */
    @PostMapping("/question/{id}/audit")
    @Transactional
    public R<Map<String, Object>> audit(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Question q = questionMapper.selectById(id);
        if (q == null) throw new BizEx(4000, "题目不存在");
        if (q.getCreateBy() != null && q.getCreateBy().equals(UserContext.id()))
            throw new BizEx(4030, "审核人不得为创建人");
        String result = String.valueOf(body.getOrDefault("result", ""));
        String reasonType = body.get("reasonType") == null ? null : String.valueOf(body.get("reasonType"));
        String reason = body.get("reason") == null ? null : String.valueOf(body.get("reason")).trim();
        if ("通过".equals(result)) {
            q.setStatus("已入库");
            if (q.getAnalysis() == null || q.getAnalysis().length() < 20)
                throw new BizEx(4000, "入库前必须填写不少于 20 字的解析");
        } else if ("退回".equals(result)) {
            if (reasonType == null || !List.of("题干不清", "答案错误", "解析缺失", "知识点错误").contains(reasonType))
                throw new BizEx(4000, "退回必须选择原因分类");
            if (reason == null || reason.length() < 5) throw new BizEx(4000, "退回说明不少于 5 字");
            q.setStatus("已退回");
        } else {
            throw new BizEx(4000, "审核结果只能是 通过/退回");
        }
        questionMapper.updateById(q);
        QuestionAudit a = new QuestionAudit();
        a.setQuestionId(id);
        a.setAuditorId(UserContext.id());
        a.setAuditResult(result);
        a.setReasonType(reasonType);
        a.setReason(reason);
        a.setSubmitTimes(1);
        a.setAuditTime(LocalDateTime.now());
        auditMapper.insert(a);
        SysMessage msg = new SysMessage();
        msg.setReceiverId(q.getCreateBy() == null ? 1L : q.getCreateBy());
        msg.setTitle("题目 " + q.getQuestionNo() + " 审核" + result);
        msg.setContent("通过".equals(result) ? "已入库，可用于组卷。" : "退回原因：" + reasonType + " - " + reason);
        msg.setBizType("QUESTION_AUDIT");
        msg.setBizId(id);
        msg.setReadFlag(0);
        messageMapper.insert(msg);
        SysOperLog log = new SysOperLog();
        log.setModule("题目管理");
        log.setOperType("审核");
        log.setBizNo(q.getQuestionNo());
        log.setContent(result + (reason == null ? "" : "，" + reason));
        log.setOperId(UserContext.id());
        log.setOperName(UserContext.name());
        log.setOperTime(LocalDateTime.now());
        logMapper.insert(log);
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("id", id);
        d.put("status", q.getStatus());
        return R.ok(d);
    }

    /** 批量导入：逐行校验题型、选项、答案格式与知识点编码，返回成功/失败明细 */
    @PostMapping("/question/import")
    @Transactional
    public R<Map<String, Object>> importQuestions(@RequestBody Map<String, Object> body) {
        Long subjectId = Long.valueOf(String.valueOf(body.getOrDefault("subjectId", 1)));
        String fileName = String.valueOf(body.getOrDefault("fileName", "批量导入.xlsx"));
        List<Map<String, Object>> rows = (List<Map<String, Object>>) body.getOrDefault("rows", List.of());
        if (rows.isEmpty()) throw new BizEx(4000, "没有可导入的数据行");
        Map<String, Long> kpByCode = new HashMap<>();
        Map<String, Long> kpByName = new HashMap<>();
        for (KnowledgePoint k : kpMapper.selectList(new QueryWrapper<KnowledgePoint>().eq("subject_id", subjectId))) {
            kpByCode.put(k.getKpNo(), k.getId());
            kpByName.put(k.getKpName(), k.getId());
        }
        int ok = 0;
        List<String> fails = new ArrayList<>();
        int seq = questionMapper.selectCount(new QueryWrapper<>()).intValue() + 1;
        for (int i = 0; i < rows.size(); i++) {
            Map<String, Object> r = rows.get(i);
            int line = i + 2;
            String type = String.valueOf(r.getOrDefault("questionType", "")).trim();
            String stem = String.valueOf(r.getOrDefault("stem", "")).trim();
            String answer = String.valueOf(r.getOrDefault("answer", "")).trim();
            String analysis = String.valueOf(r.getOrDefault("analysis", "")).trim();
            String kpKey = String.valueOf(r.getOrDefault("knowledgePoint", "")).trim();
            if (!List.of("单选", "多选", "判断", "填空", "简答", "计算").contains(type)) {
                fails.add("第 " + line + " 行：题型「" + type + "」不合法");
                continue;
            }
            if (stem.length() < 8) {
                fails.add("第 " + line + " 行：题干少于 8 字");
                continue;
            }
            Long kpId = kpByCode.getOrDefault(kpKey, kpByName.get(kpKey));
            if (kpId == null) {
                fails.add("第 " + line + " 行：知识点「" + kpKey + "」不存在于该学科");
                continue;
            }
            if ("单选".equals(type) && !answer.matches("[A-H]")) {
                fails.add("第 " + line + " 行：单选题答案必须为单个字母");
                continue;
            }
            if ("多选".equals(type)) {
                String[] parts = answer.split("[,，]");
                if (parts.length < 2) {
                    fails.add("第 " + line + " 行：多选题至少 2 个正确项");
                    continue;
                }
            }
            Question q = new Question();
            q.setQuestionNo("TM0" + subjectId + String.format("%06d", seq++));
            q.setSubjectId(subjectId);
            q.setKnowledgePointId(kpId);
            q.setQuestionType(type);
            q.setStem(stem);
            q.setAnswer(answer);
            q.setAnalysis(analysis);
            q.setDifficulty(new BigDecimal(String.valueOf(r.getOrDefault("difficulty", "0.60"))));
            q.setScore(new BigDecimal(String.valueOf(r.getOrDefault("score", "5.0"))));
            q.setSourceType(String.valueOf(r.getOrDefault("sourceType", "自建")));
            q.setCorrectRate(BigDecimal.ZERO);
            q.setStatus("待审核");
            q.setCreateBy(UserContext.id());
            questionMapper.insert(q);
            Object opts = r.get("options");
            if (opts instanceof List<?> list) {
                int idx = 0;
                for (Object o : list) {
                    String content = String.valueOf(o).trim();
                    if (content.isEmpty()) continue;
                    QuestionOption qo = new QuestionOption();
                    qo.setQuestionId(q.getId());
                    qo.setOptionLabel(String.valueOf((char) ('A' + idx)));
                    qo.setOptionContent(content);
                    qo.setIsCorrect(answer.toUpperCase().contains(String.valueOf((char) ('A' + idx))) ? 1 : 0);
                    qo.setSortNo(++idx);
                    optionMapper.insert(qo);
                }
            }
            ok++;
        }
        ImportTask t = new ImportTask();
        t.setFileName(fileName);
        t.setSubjectId(subjectId);
        t.setTotalRows(rows.size());
        t.setSuccessRows(ok);
        t.setFailRows(fails.size());
        t.setFailDetail(String.join("\n", fails));
        t.setStatus(fails.isEmpty() ? "已完成" : (ok == 0 ? "已失败" : "部分失败"));
        t.setOperatorId(UserContext.id());
        t.setFinishTime(LocalDateTime.now());
        t.setCreateBy(UserContext.id());
        importMapper.insert(t);
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("taskId", t.getId());
        d.put("total", rows.size());
        d.put("success", ok);
        d.put("fail", fails.size());
        d.put("fails", fails);
        d.put("status", t.getStatus());
        return R.ok(d);
    }

    /** 知识点树：按学科返回层级结构，附带题量与权重 */
    @GetMapping("/knowledge-point/tree")
    public R<List<Map<String, Object>>> tree(@RequestParam Long subjectId) {
        List<KnowledgePoint> all = kpMapper.selectList(new QueryWrapper<KnowledgePoint>()
                .eq("subject_id", subjectId).orderByAsc("kp_level").orderByAsc("id"));
        List<Map<String, Object>> roots = new ArrayList<>();
        for (KnowledgePoint k : all) {
            if (k.getParentId() == null || k.getParentId() == 0) roots.add(node(all, k));
        }
        return R.ok(roots);
    }

    private Map<String, Object> node(List<KnowledgePoint> all, KnowledgePoint k) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", k.getId());
        m.put("kpNo", k.getKpNo());
        m.put("kpName", k.getKpName());
        m.put("kpLevel", k.getKpLevel());
        m.put("examWeight", k.getExamWeight());
        m.put("questionCount", k.getQuestionCount());
        m.put("masteryThreshold", k.getMasteryThreshold());
        m.put("status", k.getStatus());
        m.put("parentId", k.getParentId());
        List<Map<String, Object>> ch = new ArrayList<>();
        for (KnowledgePoint c : all) if (k.getId().equals(c.getParentId())) ch.add(node(all, c));
        m.put("children", ch);
        return m;
    }

    /** 批量调整考纲权重：同一学科一级节点合计不得超过 100 */
    @PostMapping("/knowledge-point/weight-adjust")
    @Transactional
    public R<Map<String, Object>> adjustWeight(@RequestBody Map<String, Object> body) {
        Long subjectId = Long.valueOf(String.valueOf(body.getOrDefault("subjectId", 1)));
        List<Map<String, Object>> items = (List<Map<String, Object>>) body.getOrDefault("items", List.of());
        if (items.isEmpty()) throw new BizEx(4000, "没有需要调整的权重");
        BigDecimal total = BigDecimal.ZERO;
        List<KnowledgePoint> kps = kpMapper.selectList(new QueryWrapper<KnowledgePoint>()
                .eq("subject_id", subjectId).eq("kp_level", 1).eq("status", 1));
        Map<Long, BigDecimal> newWeights = new HashMap<>();
        for (KnowledgePoint k : kps) newWeights.put(k.getId(), k.getExamWeight());
        for (Map<String, Object> it : items) {
            Long id = Long.valueOf(String.valueOf(it.get("kpId")));
            BigDecimal w = new BigDecimal(String.valueOf(it.get("examWeight")));
            if (w.compareTo(BigDecimal.ZERO) < 0 || w.compareTo(new BigDecimal("100")) > 0)
                throw new BizEx(4000, "权重必须在 0 到 100 之间");
            newWeights.put(id, w);
        }
        for (BigDecimal w : newWeights.values()) total = total.add(w);
        if (total.compareTo(new BigDecimal("100")) > 0)
            throw new BizEx(4000, "一级节点权重合计 " + total + " 超过 100，禁止保存");
        for (Map<String, Object> it : items) {
            KnowledgePoint k = kpMapper.selectById(Long.valueOf(String.valueOf(it.get("kpId"))));
            if (k != null) {
                k.setExamWeight(new BigDecimal(String.valueOf(it.get("examWeight"))));
                kpMapper.updateById(k);
            }
        }
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("subjectId", subjectId);
        d.put("total", total);
        d.put("affectedPapers", "已重算该学科已发布试卷的覆盖度提示");
        return R.ok(d);
    }
}
