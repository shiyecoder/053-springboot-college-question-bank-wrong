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
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 在线练习：进入练习、交卷判分、结果详情。
 * 判分规则：单选/多选/判断/填空去空格与全角后精确比对；简答/计算按关键词命中比例给分并返回命中项。
 */
@RestController
@RequestMapping("/api")
public class PracticeController {

    private final PracticeRecordMapper recordMapper;
    private final PracticeAnswerMapper answerMapper;
    private final PaperMapper paperMapper;
    private final PaperQuestionMapper pqMapper;
    private final QuestionMapper questionMapper;
    private final QuestionOptionMapper optionMapper;
    private final WrongBookMapper wrongMapper;
    private final WrongReviewPlanMapper planMapper;

    public PracticeController(PracticeRecordMapper recordMapper, PracticeAnswerMapper answerMapper,
                              PaperMapper paperMapper, PaperQuestionMapper pqMapper, QuestionMapper questionMapper,
                              QuestionOptionMapper optionMapper, WrongBookMapper wrongMapper,
                              WrongReviewPlanMapper planMapper) {
        this.recordMapper = recordMapper;
        this.answerMapper = answerMapper;
        this.paperMapper = paperMapper;
        this.pqMapper = pqMapper;
        this.questionMapper = questionMapper;
        this.optionMapper = optionMapper;
        this.wrongMapper = wrongMapper;
        this.planMapper = planMapper;
    }

    /** 开始练习：创建进行中的练习记录，试卷状态推进为使用中 */
    @PostMapping("/practice/start")
    @Transactional
    public R<Map<String, Object>> start(@RequestBody Map<String, Object> body) {
        Long paperId = body.get("paperId") == null ? null : Long.valueOf(String.valueOf(body.get("paperId")));
        String type = String.valueOf(body.getOrDefault("practiceType", "试卷练习"));
        Paper p = paperId == null ? null : paperMapper.selectById(paperId);
        if (paperId != null && p == null) throw new BizEx(4000, "试卷不存在");
        if (p != null && !List.of("已发布", "使用中").contains(p.getStatus()))
            throw new BizEx(4001, "试卷当前状态 " + p.getStatus() + " 不可练习");
        // 幂等：同一学生同一试卷存在进行中的记录则直接复用
        PracticeRecord exist = recordMapper.selectOne(new QueryWrapper<PracticeRecord>()
                .eq("paper_id", paperId).eq("student_id", UserContext.id()).eq("status", "进行中")
                .orderByDesc("id").last("limit 1"));
        if (exist != null) return R.ok(Map.of("recordId", exist.getId(), "resumed", true));
        PracticeRecord r = new PracticeRecord();
        r.setRecordNo("LX" + LocalDateTime.now().format(com.grad.qb.config.JacksonConfig.DTF)
                .replaceAll("[^0-9]", "").substring(2, 14) + String.format("%04d", new Random().nextInt(9999)));
        r.setPaperId(paperId);
        r.setStudentId(UserContext.id());
        r.setPracticeType(type);
        r.setStartTime(LocalDateTime.now());
        r.setUsedSeconds(0);
        r.setQuestionCount(p == null ? 0 : p.getQuestionCount());
        r.setCorrectCount(0);
        r.setGotScore(BigDecimal.ZERO);
        r.setStatus("进行中");
        recordMapper.insert(r);
        if (p != null && "已发布".equals(p.getStatus())) {
            p.setStatus("使用中");
            paperMapper.updateById(p);
        }
        return R.ok(Map.of("recordId", r.getId(), "resumed", false));
    }

    /** 交卷判分：同一练习重复提交返回首次结果，不重复累加错题次数 */
    @PostMapping("/practice-record/{id}/submit")
    @Transactional
    public R<Map<String, Object>> submit(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        PracticeRecord r = recordMapper.selectById(id);
        if (r == null) throw new BizEx(4000, "练习记录不存在");
        if (!"进行中".equals(r.getStatus())) {
            // 幂等：返回首次判分结果，不重复写库
            Map<String, Object> d = new LinkedHashMap<>();
            d.put("recordId", id);
            d.put("status", r.getStatus());
            d.put("gotScore", r.getGotScore());
            d.put("correctCount", r.getCorrectCount());
            d.put("questionCount", r.getQuestionCount());
            d.put("duplicated", true);
            return R.ok(d);
        }
        List<Map<String, Object>> answers = (List<Map<String, Object>>) body.getOrDefault("answers", List.of());
        int used = body.get("usedSeconds") == null ? 0 : Integer.parseInt(String.valueOf(body.get("usedSeconds")));
        BigDecimal got = BigDecimal.ZERO;
        int correct = 0;
        List<Map<String, Object>> details = new ArrayList<>();
        for (Map<String, Object> a : answers) {
            Long qid = Long.valueOf(String.valueOf(a.get("questionId")));
            String ua = a.get("answer") == null ? "" : String.valueOf(a.get("answer"));
            Question q = questionMapper.selectById(qid);
            if (q == null) continue;
            Grade g = grade(q, ua);
            PracticeAnswer pa = new PracticeAnswer();
            pa.setRecordId(id);
            pa.setQuestionId(qid);
            pa.setStudentId(r.getStudentId());
            pa.setKnowledgePointId(q.getKnowledgePointId());
            pa.setUserAnswer(ua);
            pa.setIsCorrect(g.full ? 1 : (g.ratio > 0 ? 2 : 0));
            pa.setGotScore(g.score);
            pa.setFullScore(q.getScore());
            pa.setUsedSeconds(used / Math.max(1, answers.size()));
            answerMapper.insert(pa);
            got = got.add(g.score);
            if (g.full) correct++;
            if (!g.full) upsertWrong(r.getStudentId(), q, ua, id);
            Map<String, Object> dm = new LinkedHashMap<>();
            dm.put("questionId", qid);
            dm.put("correct", g.full);
            dm.put("ratio", g.ratio);
            dm.put("gotScore", g.score);
            dm.put("hitKeywords", g.hit);
            dm.put("standardAnswer", q.getAnswer());
            details.add(dm);
        }
        r.setSubmitTime(LocalDateTime.now());
        r.setUsedSeconds(Math.min(86400, used > 0 ? used
                : (int) Duration.between(r.getStartTime(), LocalDateTime.now()).getSeconds()));
        r.setQuestionCount(Math.max(answers.size(), r.getQuestionCount()));
        r.setCorrectCount(correct);
        r.setGotScore(got.setScale(1, RoundingMode.HALF_UP));
        r.setStatus("已交卷");
        recordMapper.updateById(r);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("recordId", id);
        data.put("status", r.getStatus());
        data.put("questionCount", r.getQuestionCount());
        data.put("correctCount", correct);
        data.put("gotScore", r.getGotScore());
        data.put("usedSeconds", r.getUsedSeconds());
        data.put("details", details);
        return R.ok(data);
    }

    /** 练习详情：题目、选项、我的作答与解析 */
    @GetMapping("/practice-record/{id}/detail")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        PracticeRecord r = recordMapper.selectById(id);
        if (r == null) throw new BizEx(4000, "练习记录不存在");
        List<PracticeAnswer> ans = answerMapper.selectList(new QueryWrapper<PracticeAnswer>().eq("record_id", id));
        Map<Long, PracticeAnswer> amap = new HashMap<>();
        for (PracticeAnswer a : ans) amap.put(a.getQuestionId(), a);
        List<Map<String, Object>> qs = new ArrayList<>();
        if (r.getPaperId() != null) {
            for (PaperQuestion pq : pqMapper.selectList(new QueryWrapper<PaperQuestion>()
                    .eq("paper_id", r.getPaperId()).orderByAsc("sort_no"))) {
                Question q = questionMapper.selectById(pq.getQuestionId());
                if (q == null) continue;
                Map<String, Object> m = new LinkedHashMap<>();
                m.put("id", q.getId());
                m.put("questionType", q.getQuestionType());
                m.put("stem", q.getStem());
                m.put("answer", q.getAnswer());
                m.put("analysis", q.getAnalysis());
                m.put("score", pq.getScore());
                m.put("options", optionMapper.selectList(new QueryWrapper<QuestionOption>()
                        .eq("question_id", q.getId()).orderByAsc("sort_no")));
                PracticeAnswer pa = amap.get(q.getId());
                m.put("myAnswer", pa == null ? null : pa.getUserAnswer());
                m.put("isCorrect", pa == null ? null : pa.getIsCorrect());
                m.put("gotScore", pa == null ? null : pa.getGotScore());
                qs.add(m);
            }
        }
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("record", r);
        data.put("questions", qs);
        return R.ok(data);
    }

    /** 作答列表（学生端练习记录页） */
    @GetMapping("/practice-record/my")
    public R<List<PracticeRecord>> my() {
        return R.ok(recordMapper.selectList(new QueryWrapper<PracticeRecord>()
                .eq("student_id", UserContext.id()).orderByDesc("start_time")));
    }

    private void upsertWrong(Long studentId, Question q, String ua, Long recordId) {
        WrongBook wb = wrongMapper.selectOne(new QueryWrapper<WrongBook>()
                .eq("student_id", studentId).eq("question_id", q.getId()));
        if (wb == null) {
            wb = new WrongBook();
            wb.setStudentId(studentId);
            wb.setQuestionId(q.getId());
            wb.setSubjectId(q.getSubjectId());
            wb.setKnowledgePointId(q.getKnowledgePointId());
            wb.setWrongCount(1);
            wb.setLastWrongTime(LocalDateTime.now());
            wb.setLastAnswer(ua.length() > 480 ? ua.substring(0, 480) : ua);
            wb.setCorrectStreak(0);
            wb.setSourceRecordId(recordId);
            wb.setStatus("未掌握");
            wb.setCreateBy(studentId);
            wrongMapper.insert(wb);
            for (int d : new int[]{1, 3, 7}) {
                WrongReviewPlan p = new WrongReviewPlan();
                p.setWrongId(wb.getId());
                p.setStudentId(studentId);
                p.setPlanDay(d);
                p.setPlanDate(LocalDate.now().plusDays(d));
                p.setDoneFlag(0);
                planMapper.insert(p);
            }
        } else {
            wb.setWrongCount(wb.getWrongCount() + 1);
            wb.setLastWrongTime(LocalDateTime.now());
            wb.setLastAnswer(ua.length() > 480 ? ua.substring(0, 480) : ua);
            wb.setCorrectStreak(0);
            wb.setStatus("未掌握");
            wb.setSourceRecordId(recordId);
            wrongMapper.updateById(wb);
        }
        Question nq = questionMapper.selectById(q.getId());
        long total = answerMapper.selectCount(new QueryWrapper<PracticeAnswer>().eq("question_id", q.getId()));
        long right = answerMapper.selectCount(new QueryWrapper<PracticeAnswer>()
                .eq("question_id", q.getId()).eq("is_correct", 1));
        if (total > 0) {
            nq.setCorrectRate(new BigDecimal(right * 100).divide(new BigDecimal(total), 2, RoundingMode.HALF_UP));
            questionMapper.updateById(nq);
        }
    }

    /** 判分：客观题精确比对，主观题关键词命中比例给分 */
    private Grade grade(Question q, String ua) {
        String type = q.getQuestionType();
        String std = q.getAnswer() == null ? "" : q.getAnswer();
        Grade g = new Grade();
        if (List.of("单选", "判断", "填空").contains(type)) {
            g.full = normalize(ua).equals(normalize(std));
            g.ratio = g.full ? 1.0 : 0.0;
            g.score = g.full ? q.getScore() : BigDecimal.ZERO;
            return g;
        }
        if ("多选".equals(type)) {
            String mine = normalizeMulti(ua);
            String right = normalizeMulti(std);
            g.full = mine.equals(right);
            if (g.full) {
                g.ratio = 1.0;
                g.score = q.getScore();
            } else if (!mine.isEmpty() && right.contains(mine.substring(0, 1))
                    && mine.split(",").length < right.split(",").length) {
                g.ratio = 0.5; // 少选给一半，选错不给分
                g.score = q.getScore().multiply(new BigDecimal("0.5")).setScale(1, RoundingMode.HALF_UP);
            }
            return g;
        }
        // 简答/计算：关键词命中比例
        List<String> keys = keywords(std);
        String mine = normalize(ua);
        List<String> hit = new ArrayList<>();
        for (String k : keys) {
            if (mine.contains(normalize(k))) hit.add(k);
        }
        g.hit = hit;
        g.ratio = keys.isEmpty() ? 0 : (double) hit.size() / keys.size();
        g.full = g.ratio >= 0.8;
        g.score = q.getScore().multiply(new BigDecimal(g.ratio)).setScale(1, RoundingMode.HALF_UP);
        return g;
    }

    private List<String> keywords(String std) {
        List<String> out = new ArrayList<>();
        for (String s : std.split("[，,、；;。\s/]+")) {
            String t = s.trim();
            if (t.length() >= 2 && !out.contains(t)) out.add(t);
        }
        return out;
    }

    private String normalize(String s) {
        if (s == null) return "";
        return s.replaceAll("[\\s\\u3000]", "").replace("，", ",").toUpperCase();
    }

    private String normalizeMulti(String s) {
        if (s == null) return "";
        String[] arr = s.replaceAll("[\\s\\u3000]", "").toUpperCase().split("[,，]");
        List<String> l = new ArrayList<>();
        for (String x : arr) if (!x.isEmpty()) l.add(x);
        Collections.sort(l);
        return String.join(",", l);
    }

    static class Grade {
        boolean full;
        double ratio;
        BigDecimal score = BigDecimal.ZERO;
        List<String> hit = new ArrayList<>();
    }
}
