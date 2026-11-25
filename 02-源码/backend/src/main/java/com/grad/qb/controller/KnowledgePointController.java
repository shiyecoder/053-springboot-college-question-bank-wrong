package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.KnowledgePoint;
import com.grad.qb.mapper.KnowledgePointMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** knowledge_point 通用增删改查 */
@RestController
@RequestMapping("/api/knowledge-point")
public class KnowledgePointController extends BaseCrudController<KnowledgePoint> {

    private final KnowledgePointMapper mapper;

    public KnowledgePointController(KnowledgePointMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<KnowledgePoint> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "kp_no", "subject_id", "parent_id", "kp_name", "kp_level", "exam_weight", "question_count", "mastery_threshold", "status", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("kp_no", "kp_name"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
