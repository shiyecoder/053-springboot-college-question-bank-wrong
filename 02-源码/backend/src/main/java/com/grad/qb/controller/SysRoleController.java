package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysRole;
import com.grad.qb.mapper.SysRoleMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_role 通用增删改查 */
@RestController
@RequestMapping("/api/role")
public class SysRoleController extends BaseCrudController<SysRole> {

    private final SysRoleMapper mapper;

    public SysRoleController(SysRoleMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysRole> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "role_name", "role_code", "data_scope", "remark", "status", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("role_name", "role_code"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
