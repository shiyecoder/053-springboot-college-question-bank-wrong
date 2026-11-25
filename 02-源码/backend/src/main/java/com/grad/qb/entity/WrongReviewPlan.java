package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/** wrong_review_plan 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("wrong_review_plan")
public class WrongReviewPlan {
    @TableId(type = IdType.AUTO) private Long id;
    private Long wrongId;
    private Long studentId;
    private Integer planDay;
    private LocalDate planDate;
    private Integer doneFlag;
    private LocalDateTime doneTime;
    private String result;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
