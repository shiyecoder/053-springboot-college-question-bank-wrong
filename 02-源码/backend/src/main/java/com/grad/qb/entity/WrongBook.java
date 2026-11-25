package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** wrong_book 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("wrong_book")
public class WrongBook {
    @TableId(type = IdType.AUTO) private Long id;
    private Long studentId;
    private Long questionId;
    private Long subjectId;
    private Long knowledgePointId;
    private Integer wrongCount;
    private LocalDateTime lastWrongTime;
    private String lastAnswer;
    private Integer correctStreak;
    private Long sourceRecordId;
    private String status;
    private String note;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
