package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** mastery_result 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("mastery_result")
public class MasteryResult {
    @TableId(type = IdType.AUTO) private Long id;
    private Long studentId;
    private Long subjectId;
    private Long knowledgePointId;
    private Long ruleId;
    private String ruleVersion;
    private BigDecimal accuracyScore;
    private BigDecimal timeScore;
    private BigDecimal redoScore;
    private BigDecimal weightScore;
    private BigDecimal reviewScore;
    private BigDecimal totalScore;
    private String level;
    private Integer sampleCount;
    private String inputSnapshot;
    private String manualLevel;
    private String manualReason;
    private Long manualBy;
    private LocalDateTime manualTime;
    private LocalDateTime calcTime;
    private Long createBy;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
