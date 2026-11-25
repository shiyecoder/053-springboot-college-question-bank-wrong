package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

/** sys_user_role 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_user_role")
public class SysUserRole {
    @TableId(type = IdType.AUTO) private Long id;
    private Long userId;
    private Long roleId;
}
