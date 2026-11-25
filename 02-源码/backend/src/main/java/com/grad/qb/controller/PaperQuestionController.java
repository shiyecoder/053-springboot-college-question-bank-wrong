package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.PaperQuestion;
import com.grad.qb.mapper.PaperQuestionMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** paper_question 通用增删改查 */
@RestController
@RequestMapping("/api/paper-question")
public class PaperQuestionController extends BaseCrudController<PaperQuestion> {

    private final PaperQuestionMapper mapper;

    public PaperQuestionController(PaperQuestionMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<PaperQuestion> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "paper_id", "question_id", "section_no", "sort_no", "score", "question_type", "knowledge_point_id", "stem_snapshot", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of(); }

    @Override
    protected String orderCol() { return "create_time"; }
}
