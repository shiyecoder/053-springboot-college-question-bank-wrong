package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** practice_answer 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("practice_answer")
public class PracticeAnswer {
    @TableId(type = IdType.AUTO) private Long id;
    private Long recordId;
    private Long questionId;
    private Long studentId;
    private Long knowledgePointId;
    private String userAnswer;
    private Integer isCorrect;
    private BigDecimal gotScore;
    private BigDecimal fullScore;
    private Integer usedSeconds;
    private Long createBy;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
