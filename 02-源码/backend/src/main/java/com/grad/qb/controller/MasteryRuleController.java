package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.MasteryRule;
import com.grad.qb.mapper.MasteryRuleMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** mastery_rule 通用增删改查 */
@RestController
@RequestMapping("/api/mastery-rule")
public class MasteryRuleController extends BaseCrudController<MasteryRule> {

    private final MasteryRuleMapper mapper;

    public MasteryRuleController(MasteryRuleMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<MasteryRule> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "rule_name", "rule_version", "w_accuracy", "w_time", "w_redo", "w_weight", "w_review", "pass_level", "good_level", "weak_level", "effect_time", "status", "remark", "create_by", "create_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("rule_name", "rule_version"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
