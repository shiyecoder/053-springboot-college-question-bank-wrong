package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.WrongReviewPlan;
import com.grad.qb.mapper.WrongReviewPlanMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** wrong_review_plan 通用增删改查 */
@RestController
@RequestMapping("/api/wrong-review-plan")
public class WrongReviewPlanController extends BaseCrudController<WrongReviewPlan> {

    private final WrongReviewPlanMapper mapper;

    public WrongReviewPlanController(WrongReviewPlanMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<WrongReviewPlan> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "wrong_id", "student_id", "plan_day", "plan_date", "done_flag", "done_time", "result", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of(); }

    @Override
    protected String orderCol() { return "create_time"; }
}
