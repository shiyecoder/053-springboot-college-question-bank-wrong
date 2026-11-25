package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** question 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("question")
public class Question {
    @TableId(type = IdType.AUTO) private Long id;
    private String questionNo;
    private Long subjectId;
    private Long knowledgePointId;
    private String questionType;
    private String stem;
    private String answer;
    private String analysis;
    private BigDecimal difficulty;
    private BigDecimal score;
    private String sourceType;
    private BigDecimal correctRate;
    private String status;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
