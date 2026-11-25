package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysDept;
import com.grad.qb.mapper.SysDeptMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_dept 通用增删改查 */
@RestController
@RequestMapping("/api/dept")
public class SysDeptController extends BaseCrudController<SysDept> {

    private final SysDeptMapper mapper;

    public SysDeptController(SysDeptMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysDept> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "parent_id", "dept_name", "leader", "sort_no", "status", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("dept_name"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
