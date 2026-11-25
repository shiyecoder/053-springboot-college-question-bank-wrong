package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.MasteryResult;
import com.grad.qb.mapper.MasteryResultMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** mastery_result 通用增删改查 */
@RestController
@RequestMapping("/api/mastery-result")
public class MasteryResultController extends BaseCrudController<MasteryResult> {

    private final MasteryResultMapper mapper;

    public MasteryResultController(MasteryResultMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<MasteryResult> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "student_id", "subject_id", "knowledge_point_id", "rule_id", "rule_version", "accuracy_score", "time_score", "redo_score", "weight_score", "review_score", "total_score", "level", "sample_count", "input_snapshot", "manual_level", "manual_reason", "manual_by", "manual_time", "calc_time", "create_by", "create_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("level"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
