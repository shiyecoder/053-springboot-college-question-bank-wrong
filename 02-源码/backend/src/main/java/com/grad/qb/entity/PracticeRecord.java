package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** practice_record 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("practice_record")
public class PracticeRecord {
    @TableId(type = IdType.AUTO) private Long id;
    private String recordNo;
    private Long paperId;
    private Long studentId;
    private String practiceType;
    private LocalDateTime startTime;
    private LocalDateTime submitTime;
    private Integer usedSeconds;
    private Integer questionCount;
    private Integer correctCount;
    private BigDecimal gotScore;
    private String status;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
