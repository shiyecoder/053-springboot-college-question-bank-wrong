package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_role 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_role")
public class SysRole {
    @TableId(type = IdType.AUTO) private Long id;
    private String roleName;
    private String roleCode;
    private String dataScope;
    private String remark;
    private Integer status;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
