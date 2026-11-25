package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.PracticeAnswer;
import com.grad.qb.mapper.PracticeAnswerMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** practice_answer 通用增删改查 */
@RestController
@RequestMapping("/api/practice-answer")
public class PracticeAnswerController extends BaseCrudController<PracticeAnswer> {

    private final PracticeAnswerMapper mapper;

    public PracticeAnswerController(PracticeAnswerMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<PracticeAnswer> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "record_id", "question_id", "student_id", "knowledge_point_id", "user_answer", "is_correct", "got_score", "full_score", "used_seconds", "create_by", "create_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("user_answer"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
