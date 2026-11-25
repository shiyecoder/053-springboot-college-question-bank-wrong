package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** question_audit 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("question_audit")
public class QuestionAudit {
    @TableId(type = IdType.AUTO) private Long id;
    private Long questionId;
    private Long auditorId;
    private String auditResult;
    private String reasonType;
    private String reason;
    private Integer submitTimes;
    private LocalDateTime auditTime;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
