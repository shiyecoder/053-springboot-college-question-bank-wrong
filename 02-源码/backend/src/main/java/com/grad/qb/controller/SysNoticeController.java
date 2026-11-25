package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysNotice;
import com.grad.qb.mapper.SysNoticeMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_notice 通用增删改查 */
@RestController
@RequestMapping("/api/notice")
public class SysNoticeController extends BaseCrudController<SysNotice> {

    private final SysNoticeMapper mapper;

    public SysNoticeController(SysNoticeMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysNotice> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "title", "content", "publish_time", "status", "create_by", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("title"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
