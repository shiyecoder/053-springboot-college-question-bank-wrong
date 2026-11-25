package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysMessage;
import com.grad.qb.mapper.SysMessageMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_message 通用增删改查 */
@RestController
@RequestMapping("/api/message")
public class SysMessageController extends BaseCrudController<SysMessage> {

    private final SysMessageMapper mapper;

    public SysMessageController(SysMessageMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysMessage> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "receiver_id", "title", "content", "biz_type", "biz_id", "read_flag", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("title"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
