package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysDictData;
import com.grad.qb.mapper.SysDictDataMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_dict_data 通用增删改查 */
@RestController
@RequestMapping("/api/dict-data")
public class SysDictDataController extends BaseCrudController<SysDictData> {

    private final SysDictDataMapper mapper;

    public SysDictDataController(SysDictDataMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysDictData> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "dict_type", "dict_label", "dict_value", "sort_no", "status"); }

    @Override
    protected List<String> keywordCols() { return List.of("dict_label", "dict_value"); }

    @Override
    protected String orderCol() { return "id"; }
}
