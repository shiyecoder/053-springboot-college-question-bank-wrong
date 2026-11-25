package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/** subject 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("subject")
public class Subject {
    @TableId(type = IdType.AUTO) private Long id;
    private String subjectNo;
    private String subjectName;
    private String eduLevel;
    private Long deptId;
    private Long ownerId;
    private Integer questionCount;
    private BigDecimal passRate;
    private Integer sortNo;
    private Integer status;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
    private Integer version;
}
