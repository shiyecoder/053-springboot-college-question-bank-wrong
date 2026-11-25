package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.qb.entity.ImportTask;
import com.grad.qb.mapper.ImportTaskMapper;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Set;

/** import_task 通用增删改查 */
@RestController
@RequestMapping("/api/import-task")
public class ImportTaskController extends BaseCrudController<ImportTask> {

    private final ImportTaskMapper mapper;

    public ImportTaskController(ImportTaskMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    protected BaseMapper<ImportTask> repo() { return mapper; }

    @Override
    protected Set<String> cols() { return Set.of("id", "file_name", "subject_id", "total_rows", "success_rows", "fail_rows", "fail_detail", "status", "operator_id", "finish_time", "create_by", "create_time", "deleted"); }

    @Override
    protected List<String> keywordCols() { return List.of("file_name"); }

    @Override
    protected String orderCol() { return "create_time"; }
}
