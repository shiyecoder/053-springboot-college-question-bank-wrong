package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.qb.common.BizEx;
import com.grad.qb.common.R;
import com.grad.qb.common.UserContext;
import com.grad.qb.entity.*;
import com.grad.qb.mapper.*;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

/** 错题本：详情（原题+我的作答+正确答案+解析）、重练（连续答对 2 次转已掌握）、移除 */
@RestController
@RequestMapping("/api/wrong-book")
public class WrongBookActionController {

    private final WrongBookMapper wrongMapper;
    private final QuestionMapper questionMapper;
    private final QuestionOptionMapper optionMapper;
    private final WrongReviewPlanMapper planMapper;

    public WrongBookActionController(WrongBookMapper wrongMapper, QuestionMapper questionMapper,
                                     QuestionOptionMapper optionMapper, WrongReviewPlanMapper planMapper) {
        this.wrongMapper = wrongMapper;
        this.questionMapper = questionMapper;
        this.optionMapper = optionMapper;
        this.planMapper = planMapper;
    }

    @GetMapping("/{id}/detail")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        WrongBook wb = wrongMapper.selectById(id);
        if (wb == null) throw new BizEx(4000, "错题不存在");
        Question q = questionMapper.selectById(wb.getQuestionId());
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("wrong", wb);
        d.put("question", q);
        d.put("options", q == null ? List.of() : optionMapper.selectList(new QueryWrapper<QuestionOption>()
                .eq("question_id", q.getId()).orderByAsc("sort_no")));
        d.put("plans", planMapper.selectList(new QueryWrapper<WrongReviewPlan>()
                .eq("wrong_id", id).orderByAsc("plan_day")));
        return R.ok(d);
    }

    /** 重练结果：答对累加连续次数，达 2 次转已掌握；答错重置 */
    @PostMapping("/{id}/review")
    @Transactional
    public R<Map<String, Object>> review(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        WrongBook wb = wrongMapper.selectById(id);
        if (wb == null) throw new BizEx(4000, "错题不存在");
        if (!wb.getStudentId().equals(UserContext.id()) && !UserContext.isAdmin())
            throw new BizEx(4030, "只能重练本人的错题");
        boolean correct = Boolean.parseBoolean(String.valueOf(body.getOrDefault("correct", false)));
        if (correct) {
            wb.setCorrectStreak((int) (wb.getCorrectStreak() == null ? 1 : wb.getCorrectStreak() + 1));
            wb.setStatus(wb.getCorrectStreak() >= 2 ? "已掌握" : "复习中");
        } else {
            wb.setCorrectStreak(0);
            wb.setStatus("未掌握");
            wb.setWrongCount(wb.getWrongCount() + 1);
            wb.setLastWrongTime(LocalDateTime.now());
        }
        wrongMapper.updateById(wb);
        // 标记今日到期的复习计划为已完成
        for (WrongReviewPlan p : planMapper.selectList(new QueryWrapper<WrongReviewPlan>()
                .eq("wrong_id", id).eq("done_flag", 0))) {
            if (!p.getPlanDate().isAfter(LocalDate.now())) {
                p.setDoneFlag(1);
                p.setDoneTime(LocalDateTime.now());
                p.setResult(correct ? "答对" : "答错");
                planMapper.updateById(p);
            }
        }
        Map<String, Object> d = new LinkedHashMap<>();
        d.put("id", id);
        d.put("status", wb.getStatus());
        d.put("correctStreak", wb.getCorrectStreak());
        return R.ok(d);
    }

    /** 手动移除：必须填写原因，历史错误次数保留用于诊断 */
    @PostMapping("/{id}/remove")
    public R<Void> remove(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        WrongBook wb = wrongMapper.selectById(id);
        if (wb == null) throw new BizEx(4000, "错题不存在");
        String reason = body.get("reason") == null ? "" : String.valueOf(body.get("reason")).trim();
        if (reason.length() < 2) throw new BizEx(4000, "请填写移除原因");
        wb.setStatus("已移除");
        wb.setNote(reason.length() > 100 ? reason.substring(0, 100) : reason);
        wrongMapper.updateById(wb);
        return R.ok();
    }

    /** 我的错题（按学科/知识点/状态筛选） */
    @GetMapping("/my")
    public R<List<Map<String, Object>>> my(@RequestParam(required = false) Long subjectId,
                                           @RequestParam(required = false) Long kpId,
                                           @RequestParam(required = false) String status) {
        QueryWrapper<WrongBook> w = new QueryWrapper<WrongBook>().eq("student_id", UserContext.id());
        if (subjectId != null) w.eq("subject_id", subjectId);
        if (kpId != null) w.eq("knowledge_point_id", kpId);
        if (status != null && !status.isBlank()) w.eq("status", status);
        w.orderByDesc("last_wrong_time");
        List<Map<String, Object>> rows = new ArrayList<>();
        for (WrongBook wb : wrongMapper.selectList(w)) {
            Question q = questionMapper.selectById(wb.getQuestionId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", wb.getId());
            m.put("questionId", wb.getQuestionId());
            m.put("stem", q == null ? "" : q.getStem());
            m.put("questionType", q == null ? "" : q.getQuestionType());
            m.put("subjectId", wb.getSubjectId());
            m.put("knowledgePointId", wb.getKnowledgePointId());
            m.put("wrongCount", wb.getWrongCount());
            m.put("lastWrongTime", wb.getLastWrongTime());
            m.put("lastAnswer", wb.getLastAnswer());
            m.put("correctStreak", wb.getCorrectStreak());
            m.put("status", wb.getStatus());
            m.put("note", wb.getNote());
            rows.add(m);
        }
        return R.ok(rows);
    }

    /** 今日到期复习清单 */
    @GetMapping("/due")
    public R<List<Map<String, Object>>> due() {
        List<WrongReviewPlan> plans = planMapper.selectList(new QueryWrapper<WrongReviewPlan>()
                .eq("student_id", UserContext.id()).eq("done_flag", 0)
                .le("plan_date", LocalDate.now()).orderByAsc("plan_date"));
        List<Map<String, Object>> rows = new ArrayList<>();
        for (WrongReviewPlan p : plans) {
            WrongBook wb = wrongMapper.selectById(p.getWrongId());
            if (wb == null) continue;
            Question q = questionMapper.selectById(wb.getQuestionId());
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("planId", p.getId());
            m.put("wrongId", p.getWrongId());
            m.put("planDay", p.getPlanDay());
            m.put("planDate", p.getPlanDate());
            m.put("stem", q == null ? "" : q.getStem());
            rows.add(m);
        }
        return R.ok(rows);
    }
}
