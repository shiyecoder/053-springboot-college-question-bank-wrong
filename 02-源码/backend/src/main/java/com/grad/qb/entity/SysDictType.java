package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_dict_type 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_dict_type")
public class SysDictType {
    @TableId(type = IdType.AUTO) private Long id;
    private String dictName;
    private String dictType;
    private Integer status;
    private LocalDateTime createTime;
}
