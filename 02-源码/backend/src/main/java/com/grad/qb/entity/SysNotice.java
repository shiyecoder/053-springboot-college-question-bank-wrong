package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_notice 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_notice")
public class SysNotice {
    @TableId(type = IdType.AUTO) private Long id;
    private String title;
    private String content;
    private LocalDateTime publishTime;
    private Integer status;
    private Long createBy;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
