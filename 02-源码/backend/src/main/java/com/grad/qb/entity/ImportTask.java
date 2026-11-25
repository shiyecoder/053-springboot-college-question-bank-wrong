package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** import_task 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("import_task")
public class ImportTask {
    @TableId(type = IdType.AUTO) private Long id;
    private String fileName;
    private Long subjectId;
    private Integer totalRows;
    private Integer successRows;
    private Integer failRows;
    private String failDetail;
    private String status;
    private Long operatorId;
    private LocalDateTime finishTime;
    private Long createBy;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
