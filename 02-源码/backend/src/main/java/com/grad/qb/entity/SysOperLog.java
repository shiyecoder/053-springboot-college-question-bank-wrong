package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_oper_log 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_oper_log")
public class SysOperLog {
    @TableId(type = IdType.AUTO) private Long id;
    private String module;
    private String operType;
    private String bizNo;
    private String content;
    private Long operId;
    private String operName;
    private LocalDateTime operTime;
    private String ip;
}
