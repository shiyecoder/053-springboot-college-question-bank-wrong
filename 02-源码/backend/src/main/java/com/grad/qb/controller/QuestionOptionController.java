package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.QuestionOption;
import com.grad.qb.mapper.QuestionOptionMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** question_option 通用增删改查 */
@RestController
@RequestMapping("/api/question-option")
public class QuestionOptionController extends BaseCrudController<QuestionOption> {

    private final QuestionOptionMapper mapper;

    public QuestionOptionController(QuestionOptionMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<QuestionOption> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "question_id", "option_label", "option_content", "is_correct", "sort_no", "image_url", "distractor_note", "chosen_count", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("option_content"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
