package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

/** sys_role_menu 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_role_menu")
public class SysRoleMenu {
    @TableId(type = IdType.AUTO) private Long id;
    private Long roleId;
    private Long menuId;
}
