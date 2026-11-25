package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** knowledge_point 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("knowledge_point")
public class KnowledgePoint {
    @TableId(type = IdType.AUTO) private Long id;
    private String kpNo;
    private Long subjectId;
    private Long parentId;
    private String kpName;
    private Integer kpLevel;
    private BigDecimal examWeight;
    private Integer questionCount;
    private BigDecimal masteryThreshold;
    private Integer status;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
