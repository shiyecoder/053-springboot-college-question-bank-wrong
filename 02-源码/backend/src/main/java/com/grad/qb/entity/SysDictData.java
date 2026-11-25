package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

/** sys_dict_data 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_dict_data")
public class SysDictData {
    @TableId(type = IdType.AUTO) private Long id;
    private String dictType;
    private String dictLabel;
    private String dictValue;
    private Integer sortNo;
    private Integer status;
}
