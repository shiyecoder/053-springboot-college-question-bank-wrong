package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysMenu;
import com.grad.qb.mapper.SysMenuMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_menu 通用增删改查 */
@RestController
@RequestMapping("/api/menu")
public class SysMenuController extends BaseCrudController<SysMenu> {

    private final SysMenuMapper mapper;

    public SysMenuController(SysMenuMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysMenu> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "parent_id", "menu_name", "path", "component", "perms", "menu_type", "icon", "sort_no", "visible", "status", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("menu_name", "path"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
