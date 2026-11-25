package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.qb.common.R;
import com.grad.qb.entity.*;
import com.grad.qb.mapper.*;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/** 统计看板：核心指标 + 6 类图表数据，默认最近 30 天，口径与明细一致 */
@RestController
@RequestMapping("/api/stats")
public class StatsController {

    private final QuestionMapper questionMapper;
    private final PracticeRecordMapper recordMapper;
    private final WrongBookMapper wrongMapper;
    private final KnowledgePointMapper kpMapper;
    private final SubjectMapper subjectMapper;
    private final MasteryResultMapper resultMapper;
    private final SysUserMapper userMapper;
    private final PracticeAnswerMapper answerMapper;

    public StatsController(QuestionMapper questionMapper, PracticeRecordMapper recordMapper, WrongBookMapper wrongMapper,
                          KnowledgePointMapper kpMapper, SubjectMapper subjectMapper, MasteryResultMapper resultMapper,
                          SysUserMapper userMapper, PracticeAnswerMapper answerMapper) {
        this.questionMapper = questionMapper;
        this.recordMapper = recordMapper;
        this.wrongMapper = wrongMapper;
        this.kpMapper = kpMapper;
        this.subjectMapper = subjectMapper;
        this.resultMapper = resultMapper;
        this.userMapper = userMapper;
        this.answerMapper = answerMapper;
    }

    @GetMapping("/overview")
    public R<Map<String, Object>> overview(@RequestParam(defaultValue = "30") int days) {
        LocalDateTime from = LocalDateTime.now().minusDays(days);
        long total = questionMapper.selectCount(new QueryWrapper<>());
        long pending = questionMapper.selectCount(new QueryWrapper<Question>().eq("status", "待审核"));
        long monthNew = questionMapper.selectCount(new QueryWrapper<Question>()
                .ge("create_time", LocalDate.now().withDayOfMonth(1).atStartOfDay()));
        long practiceCount = recordMapper.selectCount(new QueryWrapper<PracticeRecord>().ne("status", "进行中"));
        long wrongTotal = wrongMapper.selectCount(new QueryWrapper<WrongBook>().ne("status", "已移除"));
        long weakKp = resultMapper.selectList(new QueryWrapper<MasteryResult>().in("level", List.of("薄弱", "严重薄弱")))
                .stream().map(MasteryResult::getKnowledgePointId).distinct().count();
        List<PracticeRecord> recs = recordMapper.selectList(new QueryWrapper<PracticeRecord>()
                .in("status", List.of("已交卷", "已批阅")).ge("start_time", from));
        double avgRate = 0;
        if (!recs.isEmpty()) {
            double sum = 0;
            for (PracticeRecord r : recs)
                sum += r.getQuestionCount() == 0 ? 0 : (double) r.getCorrectCount() / r.getQuestionCount();
            avgRate = sum / recs.size() * 100;
        }
        long active = recs.stream().map(PracticeRecord::getStudentId).distinct().count();
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("questionTotal", total);
        d.put("pendingAudit", pending);
        d.put("monthNew", monthNew);
        d.put("practiceCount", practiceCount);
        d.put("avgCorrectRate", BigDecimal.valueOf(avgRate).setScale(1, RoundingMode.HALF_UP));
        d.put("wrongTotal", wrongTotal);
        d.put("weakKp", weakKp);
        d.put("activeStudents", active);
        return R.ok(d);
    }

    @GetMapping("/charts")
    public R<Map<String, Object>> charts(@RequestParam(defaultValue = "30") int days,
                                         @RequestParam(required = false) Long subjectId) {
        Map<String, Object> d = new LinkedHashMap<>();
        // 学科题量占比
        List<Map<String, Object>> subjectPie = new ArrayList<>();
        for (Subject s : subjectMapper.selectList(new QueryWrapper<Subject>().eq("deleted", 0))) {
            long c = questionMapper.selectCount(new QueryWrapper<Question>().eq("subject_id", s.getId()));
            if (c > 0) subjectPie.add(Map.of("name", s.getSubjectName(), "value", c));
        }
        d.put("subjectPie", subjectPie);
        // 难度分布
        int d1 = 0, d2 = 0, d3 = 0, d4 = 0;
        for (Question q : questionMapper.selectList(new QueryWrapper<>())) {
            double v = q.getDifficulty() == null ? 0.6 : q.getDifficulty().doubleValue();
            if (v < 0.35) d1++;
            else if (v < 0.55) d2++;
            else if (v < 0.75) d3++;
            else d4++;
        }
        d.put("difficulty", List.of(
                Map.of("name", "易 0.1-0.35", "value", d1), Map.of("name", "中偏易 0.35-0.55", "value", d2),
                Map.of("name", "中偏难 0.55-0.75", "value", d3), Map.of("name", "难 0.75-1.0", "value", d4)));
        // 近 N 天练习量与正确率
        List<String> axis = new ArrayList<>();
        List<Integer> counts = new ArrayList<>();
        List<Double> rates = new ArrayList<>();
        DateTimeFormatter f = DateTimeFormatter.ofPattern("MM-dd");
        // 按天全量取点，避免隔天采样与真实作答日期错位导致曲线失真
        for (int i = days - 1; i >= 0; i--) {
            LocalDate day = LocalDate.now().minusDays(i);
            List<PracticeRecord> rs = recordMapper.selectList(new QueryWrapper<PracticeRecord>()
                    .ge("start_time", day.atStartOfDay()).lt("start_time", day.plusDays(1).atStartOfDay())
                    .ne("status", "进行中"));
            axis.add(day.format(f));
            counts.add(rs.size());
            double avg = 0;
            for (PracticeRecord r : rs)
                avg += r.getQuestionCount() == 0 ? 0 : (double) r.getCorrectCount() / r.getQuestionCount();
            // 当天没有作答时给 null，折线断开而不是回落到 0，避免出现尖刺
            rates.add(rs.isEmpty() ? null : Math.round(avg / rs.size() * 1000) / 10.0);
        }
        d.put("trend", Map.of("axis", axis, "counts", counts, "rates", rates));
        // 掌握度雷达：按已有诊断结果的知识点取均分（不限层级，兼容两级知识点树）
        QueryWrapper<MasteryResult> mw = new QueryWrapper<>();
        if (subjectId != null) mw.eq("subject_id", subjectId);
        Map<Long, List<MasteryResult>> byKp = new LinkedHashMap<>();
        for (MasteryResult r : resultMapper.selectList(mw)) {
            byKp.computeIfAbsent(r.getKnowledgePointId(), x -> new ArrayList<>()).add(r);
        }
        List<Map<String, Object>> radar = new ArrayList<>();
        for (Map.Entry<Long, List<MasteryResult>> e : byKp.entrySet()) {
            KnowledgePoint k = kpMapper.selectById(e.getKey());
            // 只看末级知识点：一级节点没有直接作答，历史留痕会拉低口径
            if (k == null || k.getParentId() == null || k.getParentId() <= 0) continue;
            double avg = e.getValue().stream()
                    .filter(x -> x.getTotalScore() != null)
                    .mapToDouble(x -> x.getTotalScore().doubleValue()).average().orElse(0);
            if (avg <= 0) continue;
            radar.add(Map.of("name", k.getKpName(), "value", Math.round(avg * 10) / 10.0));
            if (radar.size() >= 6) break;
        }
        d.put("radar", radar);
        // 错题重练转化漏斗
        long notMastered = wrongMapper.selectCount(new QueryWrapper<WrongBook>().eq("status", "未掌握"));
        long reviewing = wrongMapper.selectCount(new QueryWrapper<WrongBook>().eq("status", "复习中"));
        long mastered = wrongMapper.selectCount(new QueryWrapper<WrongBook>().eq("status", "已掌握"));
        d.put("funnel", List.of(
                Map.of("name", "错题入库", "value", notMastered + reviewing + mastered),
                Map.of("name", "进入复习", "value", reviewing + mastered),
                Map.of("name", "已掌握", "value", mastered)));
        // 班级薄弱热力（按班级 × 知识点）
        List<Map<String, Object>> heat = new ArrayList<>();
        Map<String, List<MasteryResult>> byClass = new LinkedHashMap<>();
        for (SysUser u : userMapper.selectList(new QueryWrapper<SysUser>().isNotNull("class_name"))) {
            List<MasteryResult> rs = resultMapper.selectList(new QueryWrapper<MasteryResult>().eq("student_id", u.getId()));
            if (rs.isEmpty()) continue;
            byClass.computeIfAbsent(u.getClassName(), x -> new ArrayList<>()).addAll(rs);
        }
        for (Map.Entry<String, List<MasteryResult>> e : byClass.entrySet()) {
            Map<Long, List<Double>> kpScores = new LinkedHashMap<>();
            for (MasteryResult r : e.getValue())
                kpScores.computeIfAbsent(r.getKnowledgePointId(), x -> new ArrayList<>())
                        .add(r.getTotalScore().doubleValue());
            for (Map.Entry<Long, List<Double>> ke : kpScores.entrySet()) {
                KnowledgePoint k = kpMapper.selectById(ke.getKey());
                if (k == null) continue;
                Map<String, Object> m = new LinkedHashMap<>();
                m.put("className", e.getKey());
                m.put("kpName", k.getKpName());
                m.put("avg", Math.round(ke.getValue().stream().mapToDouble(x -> x).average().orElse(0) * 10) / 10.0);
                heat.add(m);
            }
        }
        d.put("heat", heat);
        // 薄弱知识点 Top
        List<Map<String, Object>> weakTop = new ArrayList<>();
        for (Map<String, Object> r : radar) {
            if (((Number) r.get("value")).doubleValue() < 70) weakTop.add(r);
        }
        d.put("weakTop", weakTop.size() > 5 ? weakTop.subList(0, 5) : weakTop);
        d.put("answerSample", answerMapper.selectCount(new QueryWrapper<>()));
        return R.ok(d);
    }
}
