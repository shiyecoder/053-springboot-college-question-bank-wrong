package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.Question;
import com.grad.qb.mapper.QuestionMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** question 通用增删改查 */
@RestController
@RequestMapping("/api/question")
public class QuestionController extends BaseCrudController<Question> {

    private final QuestionMapper mapper;

    public QuestionController(QuestionMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<Question> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "question_no", "subject_id", "knowledge_point_id", "question_type", "stem", "answer", "analysis", "difficulty", "score", "source_type", "correct_rate", "status", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("question_no", "stem"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
