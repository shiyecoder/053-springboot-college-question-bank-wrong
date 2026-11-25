package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysOperLog;
import com.grad.qb.mapper.SysOperLogMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_oper_log 通用增删改查 */
@RestController
@RequestMapping("/api/oper-log")
public class SysOperLogController extends BaseCrudController<SysOperLog> {

    private final SysOperLogMapper mapper;

    public SysOperLogController(SysOperLogMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysOperLog> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "module", "oper_type", "biz_no", "content", "oper_id", "oper_name", "oper_time", "ip"); }

    @Override
    protected List<String> keywordCols() { return List.of("content", "module"); }

    @Override
    protected String orderCol() { return "id"; }
}
