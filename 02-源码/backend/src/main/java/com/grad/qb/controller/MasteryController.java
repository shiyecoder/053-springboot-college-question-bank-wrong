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
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 创新点：知识点掌握度诊断。
 * 五项因子加权：近30天正确率 40%、平均耗时比 15%、错题重做表现 20%、考纲权重 15%、复习及时率 10%。
 * 每次计算保存输入快照、规则版本、各因子得分与总分，结果可追溯；支持人工修正且原始结果不被覆盖。
 */
@RestController
@RequestMapping("/api")
public class MasteryController {

    private final MasteryRuleMapper ruleMapper;
    private final MasteryResultMapper resultMapper;
    private final KnowledgePointMapper kpMapper;
    private final SubjectMapper subjectMapper;
    private final PracticeAnswerMapper answerMapper;
    private final WrongBookMapper wrongMapper;
    private final WrongReviewPlanMapper planMapper;
    private final SysUserMapper userMapper;
    private final SysUserRoleMapper userRoleMapper;
    private final SysMessageMapper messageMapper;

    public MasteryController(MasteryRuleMapper ruleMapper, MasteryResultMapper resultMapper,
                             KnowledgePointMapper kpMapper, SubjectMapper subjectMapper,
                             PracticeAnswerMapper answerMapper, WrongBookMapper wrongMapper,
                             WrongReviewPlanMapper planMapper, SysUserMapper userMapper,
                             SysUserRoleMapper userRoleMapper, SysMessageMapper messageMapper) {
        this.ruleMapper = ruleMapper;
        this.resultMapper = resultMapper;
        this.kpMapper = kpMapper;
        this.subjectMapper = subjectMapper;
        this.answerMapper = answerMapper;
        this.wrongMapper = wrongMapper;
        this.planMapper = planMapper;
        this.userMapper = userMapper;
        this.userRoleMapper = userRoleMapper;
        this.messageMapper = messageMapper;
    }

    /** 当前生效规则；无生效规则时回退到最新一条 */
    private MasteryRule activeRule() {
        MasteryRule r = ruleMapper.selectOne(new QueryWrapper<MasteryRule>()
                .eq("status", "生效中").orderByDesc("id").last("limit 1"));
        return r != null ? r : ruleMapper.selectOne(new QueryWrapper<MasteryRule>().orderByDesc("id").last("limit 1"));
    }

    /**
     * 诊断单元只取叶子知识点：作答记录挂在最末级知识点上，
     * 若把带子节点的一级节点也当诊断单元，其样本恒为 0，会误显示"未测"。
     */
    private List<KnowledgePoint> leafPoints(Long subjectId) {
        List<KnowledgePoint> all = kpMapper.selectList(new QueryWrapper<KnowledgePoint>()
                .eq("subject_id", subjectId).eq("status", 1).orderByAsc("kp_level").orderByAsc("id"));
        Set<Long> parents = new HashSet<>();
        for (KnowledgePoint k : all) {
            if (k.getParentId() != null && k.getParentId() > 0) parents.add(k.getParentId());
        }
        List<KnowledgePoint> leaves = new ArrayList<>();
        for (KnowledgePoint k : all) {
            if (!parents.contains(k.getId())) leaves.add(k);
        }
        return leaves;
    }

    /** 学生掌握度诊断：按知识点输出五因子、总分、等级、样本量与结论 */
    @GetMapping("/student/{id}/mastery")
    public R<Map<String, Object>> student(@PathVariable Long id, @RequestParam(defaultValue = "1") Long subjectId) {
        if (!id.equals(UserContext.id()) && !List.of("TEACHER", "AUDITOR", "SECRETARY", "ADMIN").contains(UserContext.role()))
            throw new BizEx(4030, "只能查看本人或所带学生的诊断");
        MasteryRule rule = activeRule();
        List<KnowledgePoint> kps = leafPoints(subjectId);
        List<Map<String, Object>> rows = new ArrayList<>();
        List<Map<String, Object>> weak = new ArrayList<>();
        BigDecimal sum = BigDecimal.ZERO;
        int measured = 0;
        for (KnowledgePoint k : kps) {
            Map<String, Object> row = compute(id, k, rule);
            rows.add(row);
            String level = String.valueOf(row.get("level"));
            if (!"未测".equals(level)) {
                sum = sum.add((BigDecimal) row.get("totalScore"));
                measured++;
            }
            if (List.of("薄弱", "严重薄弱").contains(level)) weak.add(row);
        }
        weak.sort(Comparator.comparing(r -> ((BigDecimal) r.get("totalScore"))));
        Subject s = subjectMapper.selectById(subjectId);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("studentId", id);
        data.put("studentName", name(id));
        data.put("subjectId", subjectId);
        data.put("subjectName", s == null ? "" : s.getSubjectName());
        data.put("ruleVersion", rule == null ? "-" : rule.getRuleVersion());
        data.put("ruleId", rule == null ? null : rule.getId());
        data.put("average", measured == 0 ? BigDecimal.ZERO
                : sum.divide(new BigDecimal(measured), 1, RoundingMode.HALF_UP));
        data.put("measuredCount", measured);
        data.put("totalCount", kps.size());
        data.put("items", rows);
        data.put("weak", weak.size() > 6 ? weak.subList(0, 6) : weak);
        return R.ok(data);
    }

    /**
     * 单知识点五因子计算（纯函数，便于复现）：
     * 正确率按近 30 天作答；耗时比 = 平均用时 / 标准用时；重做表现取错题重练正确率；
     * 考纲权重按同学科一级节点最大权重归一；复习及时率取 1/3/7 天计划完成比例。
     */
    private Map<String, Object> compute(Long studentId, KnowledgePoint k, MasteryRule rule) {
        int wAcc = rule == null ? 40 : rule.getWAccuracy().intValue();
        int wTime = rule == null ? 15 : rule.getWTime().intValue();
        int wRedo = rule == null ? 20 : rule.getWRedo().intValue();
        int wWeight = rule == null ? 15 : rule.getWWeight().intValue();
        int wReview = rule == null ? 10 : rule.getWReview().intValue();

        LocalDateTime from = LocalDateTime.now().minusDays(30);
        List<PracticeAnswer> ans = answerMapper.selectList(new QueryWrapper<PracticeAnswer>()
                .eq("student_id", studentId).eq("knowledge_point_id", k.getId()).ge("create_time", from));
        int sample = ans.size();
        // 1) 正确率
        double accScore = 0;
        double accRate = 0;
        int usedSum = 0;
        for (PracticeAnswer a : ans) {
            if (a.getIsCorrect() != null && a.getIsCorrect() == 1) accScore++;
            usedSum += a.getUsedSeconds() == null ? 0 : a.getUsedSeconds();
        }
        if (sample > 0) {
            accRate = accScore / sample;
            accScore = accRate * 100;
        }
        // 2) 耗时比：标准用时按难度折算 60~180 秒
        double timeScore = 0;
        if (sample > 0) {
            double avg = usedSum / (double) sample;
            double standard = 90;
            double ratio = avg / standard;
            if (ratio <= 0.8) timeScore = 100;
            else if (ratio <= 1.0) timeScore = 100 - (ratio - 0.8) * 75;
            else if (ratio < 2.0) timeScore = 85 - (ratio - 1.0) * 85;
            else timeScore = 0;
            timeScore = Math.max(0, Math.min(100, timeScore));
        }
        // 3) 错题重做表现（无错题按 70 基准）
        List<WrongBook> wbs = wrongMapper.selectList(new QueryWrapper<WrongBook>()
                .eq("student_id", studentId).eq("knowledge_point_id", k.getId()).ne("status", "已移除"));
        double redoScore = 70;
        int redoCount = 0;
        if (!wbs.isEmpty()) {
            double s = 0;
            for (WrongBook wb : wbs) {
                if ("已掌握".equals(wb.getStatus())) s += 100;
                else if ("复习中".equals(wb.getStatus())) s += 65;
                else s += 30;
                redoCount += wb.getWrongCount() == null ? 1 : wb.getWrongCount();
            }
            redoScore = s / wbs.size();
        }
        // 4) 考纲权重归一化（相对同学科一级节点最大值）
        double maxW = kpMapper.selectList(new QueryWrapper<KnowledgePoint>()
                        .eq("subject_id", k.getSubjectId()).eq("kp_level", 1).eq("status", 1))
                .stream().mapToDouble(x -> x.getExamWeight() == null ? 0 : x.getExamWeight().doubleValue()).max().orElse(100);
        double weightScore = maxW <= 0 ? 50 : Math.min(100, k.getExamWeight().doubleValue() / maxW * 100);
        // 5) 复习及时率（1/3/7 天计划完成比例）
        List<Long> wids = wbs.stream().map(WrongBook::getId).toList();
        double reviewScore = 0;
        int planTotal = 0, planDone = 0;
        if (!wids.isEmpty()) {
            List<WrongReviewPlan> plans = planMapper.selectList(new QueryWrapper<WrongReviewPlan>()
                    .in("wrong_id", wids).le("plan_date", LocalDate.now()));
            planTotal = plans.size();
            for (WrongReviewPlan p : plans) if (p.getDoneFlag() != null && p.getDoneFlag() == 1) planDone++;
            reviewScore = planTotal == 0 ? 0 : planDone * 100.0 / planTotal;
        }
        double total = accScore * wAcc / 100.0 + timeScore * wTime / 100.0 + redoScore * wRedo / 100.0
                + weightScore * wWeight / 100.0 + reviewScore * wReview / 100.0;
        BigDecimal totalScore = BigDecimal.valueOf(total).setScale(1, RoundingMode.HALF_UP);
        double pass = rule == null ? 85 : rule.getPassLevel().doubleValue();
        double good = rule == null ? 70 : rule.getGoodLevel().doubleValue();
        double weakLine = rule == null ? 50 : rule.getWeakLevel().doubleValue();
        String level;
        if (sample == 0) level = "未测";
        else if (totalScore.doubleValue() >= pass) level = "已掌握";
        else if (totalScore.doubleValue() >= good) level = "基本掌握";
        else if (totalScore.doubleValue() >= weakLine) level = "薄弱";
        else level = "严重薄弱";

        MasteryResult saved = resultMapper.selectOne(new QueryWrapper<MasteryResult>()
                .eq("student_id", studentId).eq("knowledge_point_id", k.getId())
                .orderByDesc("id").last("limit 1"));

        Map<String, Object> m = new LinkedHashMap<>();
        m.put("kpId", k.getId());
        m.put("kpName", k.getKpName());
        m.put("kpLevel", k.getKpLevel());
        m.put("examWeight", k.getExamWeight());
        m.put("resultId", saved == null ? null : saved.getId());
        m.put("ruleVersion", saved == null ? (rule == null ? "-" : rule.getRuleVersion()) : saved.getRuleVersion());
        m.put("accuracyRate", BigDecimal.valueOf(accRate * 100).setScale(1, RoundingMode.HALF_UP));
        m.put("accuracyScore", BigDecimal.valueOf(accScore).setScale(1, RoundingMode.HALF_UP));
        m.put("timeScore", BigDecimal.valueOf(timeScore).setScale(1, RoundingMode.HALF_UP));
        m.put("redoScore", BigDecimal.valueOf(redoScore).setScale(1, RoundingMode.HALF_UP));
        m.put("weightScore", BigDecimal.valueOf(weightScore).setScale(1, RoundingMode.HALF_UP));
        m.put("reviewScore", BigDecimal.valueOf(reviewScore).setScale(1, RoundingMode.HALF_UP));
        m.put("totalScore", totalScore);
        m.put("level", saved != null && saved.getManualLevel() != null ? saved.getManualLevel() : level);
        m.put("rawLevel", level);
        m.put("manual", saved != null && saved.getManualLevel() != null);
        m.put("manualReason", saved == null ? null : saved.getManualReason());
        m.put("sampleCount", sample);
        m.put("insufficient", sample < 5);
        m.put("planDone", planDone);
        m.put("planTotal", planTotal);
        m.put("redoCount", redoCount);
        m.put("suggestion", suggestion(level, sample, accRate, timeScore, redoScore, reviewScore));
        return m;
    }

    private String suggestion(String level, int sample, double acc, double time, double redo, double review) {
        if (sample == 0) return "近 30 天没有作答记录，无法诊断，先完成一次知识点练习";
        if (sample < 5) return "样本仅 " + sample + " 次，结论仅供参考，建议再完成 5 道同类题";
        if ("已掌握".equals(level)) return "正确率与重做表现稳定，减少同类题推送，进入下一知识点";
        if ("基本掌握".equals(level)) return "偶发错误，建议推送 3 道变式题巩固";
        StringBuilder sb = new StringBuilder();
        if (acc < 0.6) sb.append("正确率偏低（").append(Math.round(acc * 100)).append("%），先重做基础题；");
        if (time < 40) sb.append("平均用时明显超过标准时长，注意解题熟练度；");
        if (redo < 60) sb.append("错题重做未通过，需重新看解析；");
        if (review < 60) sb.append("复习计划完成不及时，先补齐 1/3/7 天计划；");
        if (sb.length() == 0) sb.append("综合表现接近分档线，建议补 10 道同类题");
        return sb.toString();
    }

    /** 重算并落库：保存输入快照与规则版本，供追溯与重放 */
    @PostMapping("/mastery/recompute")
    @Transactional
    public R<Map<String, Object>> recompute(@RequestBody Map<String, Object> body) {
        Long studentId = Long.valueOf(String.valueOf(body.getOrDefault("studentId", UserContext.id())));
        Long subjectId = Long.valueOf(String.valueOf(body.getOrDefault("subjectId", 1)));
        return R.ok(recomputeFor(studentId, subjectId, UserContext.id()));
    }

    /** 全量重算：管理员手动触发，等价于每日凌晨的定时任务 */
    @PostMapping("/mastery/recompute-all")
    public R<Map<String, Object>> recomputeAll() {
        if (!"ADMIN".equals(UserContext.role())) throw new BizEx(4030, "仅系统管理员可执行全量重算");
        Map<String, Object> stat = recomputeAllQuiet(1L);
        return R.ok(stat);
    }

    /**
     * 全量重算所有学生的所有学科，供定时任务与管理员入口复用。
     * 变化幅度超过 10 分的知识点会生成教师复核消息。
     */
    public Map<String, Object> recomputeAllQuiet(Long operatorId) {
        int students = 0;
        int rows = 0;
        int changed = 0;
        // 学生名单：学生角色对应的用户
        Set<Long> studentIds = new LinkedHashSet<>();
        for (SysUserRole ur : userRoleMapper.selectList(new QueryWrapper<SysUserRole>().eq("role_id", 5))) {
            studentIds.add(ur.getUserId());
        }
        List<Subject> subjects = subjectMapper.selectList(new QueryWrapper<Subject>().eq("status", 1));
        for (Long sid : studentIds) {
            students++;
            for (Subject s : subjects) {
                Map<String, Object> d = recomputeFor(sid, s.getId(), operatorId);
                rows += (Integer) d.get("count");
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> changes = (List<Map<String, Object>>) d.get("changes");
                changed += changes.size();
                for (Map<String, Object> c : changes) {
                    SysMessage msg = new SysMessage();
                    msg.setReceiverId(s.getOwnerId());
                    msg.setTitle("掌握度重算变更提醒");
                    msg.setContent(String.format("学生 %s 在知识点「%s」的掌握度由 %s 变为 %s（变化 %s 分，超过 10 分阈值），请复核诊断结果。",
                            name(sid), c.get("kpName"), c.get("before"), c.get("after"), c.get("diff")));
                    msg.setBizType("诊断提醒");
                    msg.setReadFlag(0);
                    msg.setCreateTime(LocalDateTime.now());
                    messageMapper.insert(msg);
                }
            }
        }
        Map<String, Object> stat = new LinkedHashMap<>();
        stat.put("students", students);
        stat.put("rows", rows);
        stat.put("changed", changed);
        stat.put("calcTime", LocalDateTime.now().toString());
        return stat;
    }

    /** 单个学生单学科重算：返回条目数、规则版本与变化明细 */
    public Map<String, Object> recomputeFor(Long studentId, Long subjectId, Long operatorId) {
        MasteryRule rule = activeRule();
        if (rule == null) throw new BizEx(4001, "尚未配置诊断规则");
        List<KnowledgePoint> kps = leafPoints(subjectId);
        List<Map<String, Object>> changes = new ArrayList<>();
        int n = 0;
        for (KnowledgePoint k : kps) {
            Map<String, Object> row = compute(studentId, k, rule);
            BigDecimal total = (BigDecimal) row.get("totalScore");
            // 上一次诊断结果，用于计算变化幅度
            MasteryResult last = resultMapper.selectOne(new QueryWrapper<MasteryResult>()
                    .eq("student_id", studentId).eq("knowledge_point_id", k.getId())
                    .orderByDesc("calc_time").orderByDesc("id").last("limit 1"));
            MasteryResult mr = new MasteryResult();
            mr.setStudentId(studentId);
            mr.setSubjectId(subjectId);
            mr.setKnowledgePointId(k.getId());
            mr.setRuleId(rule.getId());
            mr.setRuleVersion(rule.getRuleVersion());
            mr.setAccuracyScore((BigDecimal) row.get("accuracyScore"));
            mr.setTimeScore((BigDecimal) row.get("timeScore"));
            mr.setRedoScore((BigDecimal) row.get("redoScore"));
            mr.setWeightScore((BigDecimal) row.get("weightScore"));
            mr.setReviewScore((BigDecimal) row.get("reviewScore"));
            mr.setTotalScore(total);
            mr.setLevel(String.valueOf(row.get("rawLevel")));
            mr.setSampleCount((Integer) row.get("sampleCount"));
            mr.setInputSnapshot(String.format(
                    "{\"accuracyRate\":%s,\"timeScore\":%s,\"redoScore\":%s,\"examWeight\":%s,\"reviewRate\":%s,\"sample\":%d,\"planDone\":%s,\"planTotal\":%s}",
                    row.get("accuracyRate"), row.get("timeScore"), row.get("redoScore"), k.getExamWeight(),
                    row.get("reviewScore"), row.get("sampleCount"), row.get("planDone"), row.get("planTotal")));
            mr.setCalcTime(LocalDateTime.now());
            mr.setCreateBy(operatorId);
            resultMapper.insert(mr);
            n++;
            if (last != null && last.getTotalScore() != null && total != null) {
                BigDecimal diff = total.subtract(last.getTotalScore());
                if (diff.abs().compareTo(BigDecimal.TEN) > 0) {
                    Map<String, Object> c = new LinkedHashMap<>();
                    c.put("knowledgePointId", k.getId());
                    c.put("kpName", k.getKpName());
                    c.put("before", last.getTotalScore());
                    c.put("after", total);
                    c.put("diff", diff.setScale(1, RoundingMode.HALF_UP));
                    changes.add(c);
                }
            }
        }
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("studentId", studentId);
        d.put("subjectId", subjectId);
        d.put("ruleVersion", rule.getRuleVersion());
        d.put("count", n);
        d.put("changes", changes);
        return d;
    }

    /** 人工修正：原因不少于 5 字，原始 level 保留 */
    @PostMapping("/mastery/{id}/manual")
    public R<MasteryResult> manual(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        MasteryResult mr = resultMapper.selectById(id);
        if (mr == null) throw new BizEx(4000, "诊断结果不存在");
        String level = String.valueOf(body.getOrDefault("level", ""));
        String reason = String.valueOf(body.getOrDefault("reason", "")).trim();
        if (!List.of("已掌握", "基本掌握", "薄弱", "严重薄弱").contains(level))
            throw new BizEx(4000, "请选择有效的掌握等级");
        if (reason.length() < 5) throw new BizEx(4000, "人工修正必须填写不少于 5 字的原因");
        mr.setManualLevel(level);
        mr.setManualReason(reason);
        mr.setManualBy(UserContext.id());
        mr.setManualTime(LocalDateTime.now());
        resultMapper.updateById(mr);
        return R.ok(mr);
    }

    /** 规则配置：权重合计必须等于 100% */
    @GetMapping("/mastery/rule")
    public R<Map<String, Object>> rule() {
        MasteryRule active = activeRule();
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("active", active);
        d.put("versions", ruleMapper.selectList(new QueryWrapper<MasteryRule>().orderByDesc("id")));
        return R.ok(d);
    }

    @PostMapping("/mastery/rule")
    @Transactional
    public R<MasteryRule> saveRule(@RequestBody MasteryRule body) {
        BigDecimal sum = body.getWAccuracy().add(body.getWTime()).add(body.getWRedo())
                .add(body.getWWeight()).add(body.getWReview());
        if (sum.compareTo(new BigDecimal("100")) != 0)
            throw new BizEx(4000, "五项因子权重合计必须等于 100%，当前为 " + sum);
        MasteryRule old = activeRule();
        if (old != null) {
            old.setStatus("已归档");
            ruleMapper.updateById(old);
        }
        body.setId(null);
        body.setStatus("生效中");
        body.setEffectTime(LocalDateTime.now());
        String ver = old == null ? "v1" : "v" + (Integer.parseInt(old.getRuleVersion().replace("v", "")) + 1);
        body.setRuleVersion(ver);
        body.setCreateBy(UserContext.id());
        if (body.getPassLevel() == null) body.setPassLevel(new BigDecimal("85"));
        if (body.getGoodLevel() == null) body.setGoodLevel(new BigDecimal("70"));
        if (body.getWeakLevel() == null) body.setWeakLevel(new BigDecimal("50"));
        ruleMapper.insert(body);
        return R.ok(body);
    }

    /** 班级掌握度：按学生聚合，供教师端排名与热力 */
    @GetMapping("/mastery/class")
    public R<Map<String, Object>> classStat(@RequestParam(defaultValue = "1") Long subjectId,
                                            @RequestParam(required = false) String className) {
        QueryWrapper<SysUser> uw = new QueryWrapper<SysUser>().eq("deleted", 0);
        if (className != null && !className.isBlank()) uw.eq("class_name", className);
        List<SysUser> students = userMapper.selectList(uw);
        List<Map<String, Object>> rows = new ArrayList<>();
        for (SysUser u : students) {
            if (u.getClassName() == null) continue;
            List<MasteryResult> rs = resultMapper.selectList(new QueryWrapper<MasteryResult>()
                    .eq("student_id", u.getId()).eq("subject_id", subjectId));
            if (rs.isEmpty()) continue;
            double avg = rs.stream().filter(r -> !"未测".equals(r.getLevel()))
                    .mapToDouble(r -> r.getTotalScore().doubleValue()).average().orElse(0);
            List<String> weak = new ArrayList<>();
            for (MasteryResult r : rs) {
                String lv = r.getManualLevel() != null ? r.getManualLevel() : r.getLevel();
                if (List.of("薄弱", "严重薄弱").contains(lv)) {
                    KnowledgePoint k = kpMapper.selectById(r.getKnowledgePointId());
                    if (k != null) weak.add(k.getKpName());
                }
            }
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("studentId", u.getId());
            m.put("studentNo", u.getUsername());
            m.put("name", u.getRealName());
            m.put("className", u.getClassName());
            m.put("mastery", BigDecimal.valueOf(avg).setScale(1, RoundingMode.HALF_UP));
            m.put("measured", rs.size());
            m.put("weak", weak.size() > 3 ? weak.subList(0, 3) : weak);
            rows.add(m);
        }
        rows.sort((a, b) -> ((BigDecimal) b.get("mastery")).compareTo((BigDecimal) a.get("mastery")));
        List<KnowledgePoint> kps = kpMapper.selectList(new QueryWrapper<KnowledgePoint>()
                .eq("subject_id", subjectId).eq("kp_level", 3).eq("status", 1));
        List<Map<String, Object>> cells = new ArrayList<>();
        for (KnowledgePoint k : kps) {
            List<MasteryResult> rs = resultMapper.selectList(new QueryWrapper<MasteryResult>()
                    .eq("subject_id", subjectId).eq("knowledge_point_id", k.getId()));
            if (rs.isEmpty()) continue;
            double avg = rs.stream().mapToDouble(r -> r.getTotalScore().doubleValue()).average().orElse(0);
            Map<String, Object> c = new LinkedHashMap<>();
            c.put("kpName", k.getKpName());
            c.put("avg", BigDecimal.valueOf(avg).setScale(1, RoundingMode.HALF_UP));
            c.put("sample", rs.size());
            cells.add(c);
        }
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("students", rows);
        d.put("kps", cells);
        return R.ok(d);
    }

    private String name(Long id) {
        SysUser u = userMapper.selectById(id);
        return u == null ? "-" : u.getRealName();
    }
}
