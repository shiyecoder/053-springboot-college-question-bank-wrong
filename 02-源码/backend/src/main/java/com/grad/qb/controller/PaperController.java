package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.Paper;
import com.grad.qb.mapper.PaperMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** paper 通用增删改查 */
@RestController
@RequestMapping("/api/paper")
public class PaperController extends BaseCrudController<Paper> {

    private final PaperMapper mapper;

    public PaperController(PaperMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<Paper> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "paper_no", "paper_name", "subject_id", "build_mode", "question_count", "total_score", "duration_min", "difficulty_avg", "random_rule", "creator_id", "status", "reject_reason", "create_by", "create_time", "update_by", "update_time", "deleted", "version"); }

    @Override
    protected List<String> keywordCols() { return List.of("paper_no", "paper_name"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
