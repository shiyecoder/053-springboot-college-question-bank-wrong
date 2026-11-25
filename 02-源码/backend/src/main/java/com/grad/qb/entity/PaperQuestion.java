package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** paper_question 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("paper_question")
public class PaperQuestion {
    @TableId(type = IdType.AUTO) private Long id;
    private Long paperId;
    private Long questionId;
    private Integer sectionNo;
    private Integer sortNo;
    private BigDecimal score;
    private String questionType;
    private Long knowledgePointId;
    private String stemSnapshot;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
