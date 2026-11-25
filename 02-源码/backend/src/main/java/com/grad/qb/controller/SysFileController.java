package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.SysFile;
import com.grad.qb.mapper.SysFileMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** sys_file 通用增删改查 */
@RestController
@RequestMapping("/api/file-meta")
public class SysFileController extends BaseCrudController<SysFile> {

    private final SysFileMapper mapper;

    public SysFileController(SysFileMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<SysFile> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "file_name", "file_path", "file_size", "file_type", "biz_type", "biz_id", "uploader_id", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("file_name"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
