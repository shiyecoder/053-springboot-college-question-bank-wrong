package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysDictType;
import com.grad.qb.mapper.SysDictTypeMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_dict_type 通用增删改查 */
@RestController
@RequestMapping("/api/dict-type")
public class SysDictTypeController extends BaseCrudController<SysDictType> {

    private final SysDictTypeMapper mapper;

    public SysDictTypeController(SysDictTypeMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysDictType> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "dict_name", "dict_type", "status", "create_time"); }

    @Override
    protected List<String> keywordCols() { return List.of("dict_name", "dict_type"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
