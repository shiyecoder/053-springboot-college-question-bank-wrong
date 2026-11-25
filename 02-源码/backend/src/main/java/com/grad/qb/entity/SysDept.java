package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_dept 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_dept")
public class SysDept {
    @TableId(type = IdType.AUTO) private Long id;
    private Long parentId;
    private String deptName;
    private String leader;
    private Integer sortNo;
    private Integer status;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
