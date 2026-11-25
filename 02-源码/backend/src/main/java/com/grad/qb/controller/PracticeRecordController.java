package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.PracticeRecord;
import com.grad.qb.mapper.PracticeRecordMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** practice_record 通用增删改查 */
@RestController
@RequestMapping("/api/practice-record")
public class PracticeRecordController extends BaseCrudController<PracticeRecord> {

    private final PracticeRecordMapper mapper;

    public PracticeRecordController(PracticeRecordMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<PracticeRecord> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "record_no", "paper_id", "student_id", "practice_type", "start_time", "submit_time", "used_seconds", "question_count", "correct_count", "got_score", "status", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("record_no"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
