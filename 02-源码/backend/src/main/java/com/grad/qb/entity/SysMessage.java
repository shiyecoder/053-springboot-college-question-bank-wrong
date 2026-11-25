package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_message 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_message")
public class SysMessage {
    @TableId(type = IdType.AUTO) private Long id;
    private Long receiverId;
    private String title;
    private String content;
    private String bizType;
    private Long bizId;
    private Integer readFlag;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
