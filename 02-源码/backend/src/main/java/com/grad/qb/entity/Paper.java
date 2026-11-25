package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** paper 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("paper")
public class Paper {
    @TableId(type = IdType.AUTO) private Long id;
    private String paperNo;
    private String paperName;
    private Long subjectId;
    private String buildMode;
    private Integer questionCount;
    private BigDecimal totalScore;
    private Integer durationMin;
    private BigDecimal difficultyAvg;
    private String randomRule;
    private Long creatorId;
    private String status;
    private String rejectReason;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
