package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_menu 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_menu")
public class SysMenu {
    @TableId(type = IdType.AUTO) private Long id;
    private Long parentId;
    private String menuName;
    private String path;
    private String component;
    private String perms;
    private String menuType;
    private String icon;
    private Integer sortNo;
    private Integer visible;
    private Integer status;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
