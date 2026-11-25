package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.QuestionAudit;
import com.grad.qb.mapper.QuestionAuditMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** question_audit 通用增删改查 */
@RestController
@RequestMapping("/api/question-audit")
public class QuestionAuditController extends BaseCrudController<QuestionAudit> {

    private final QuestionAuditMapper mapper;

    public QuestionAuditController(QuestionAuditMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<QuestionAudit> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "question_id", "auditor_id", "audit_result", "reason_type", "reason", "submit_times", "audit_time", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("reason"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
