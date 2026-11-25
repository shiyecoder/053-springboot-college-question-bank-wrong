package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** question_option 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("question_option")
public class QuestionOption {
    @TableId(type = IdType.AUTO) private Long id;
    private Long questionId;
    private String optionLabel;
    private String optionContent;
    private Integer isCorrect;
    private Integer sortNo;
    private String imageUrl;
    private String distractorNote;
    private Integer chosenCount;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
