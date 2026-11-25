package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** mastery_rule 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("mastery_rule")
public class MasteryRule {
    @TableId(type = IdType.AUTO) private Long id;
    private String ruleName;
    private String ruleVersion;
    private BigDecimal wAccuracy;
    private BigDecimal wTime;
    private BigDecimal wRedo;
    private BigDecimal wWeight;
    private BigDecimal wReview;
    private BigDecimal passLevel;
    private BigDecimal goodLevel;
    private BigDecimal weakLevel;
    private LocalDateTime effectTime;
    private String status;
    private String remark;
    private Long createBy;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
