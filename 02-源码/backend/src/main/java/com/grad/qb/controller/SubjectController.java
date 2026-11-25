package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.Subject;
import com.grad.qb.mapper.SubjectMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** subject 通用增删改查 */
@RestController
@RequestMapping("/api/subject")
public class SubjectController extends BaseCrudController<Subject> {

    private final SubjectMapper mapper;

    public SubjectController(SubjectMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<Subject> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "subject_no", "subject_name", "edu_level", "dept_id", "owner_id", "question_count", "pass_rate", "sort_no", "status", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("subject_no", "subject_name"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
