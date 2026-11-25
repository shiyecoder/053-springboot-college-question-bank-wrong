package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.WrongBook;
import com.grad.qb.mapper.WrongBookMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** wrong_book 通用增删改查 */
@RestController
@RequestMapping("/api/wrong-book")
public class WrongBookController extends BaseCrudController<WrongBook> {

    private final WrongBookMapper mapper;

    public WrongBookController(WrongBookMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<WrongBook> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "student_id", "question_id", "subject_id", "knowledge_point_id", "wrong_count", "last_wrong_time", "last_answer", "correct_streak", "source_record_id", "status", "note", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("last_answer"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
