package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_file 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_file")
public class SysFile {
    @TableId(type = IdType.AUTO) private Long id;
    private String fileName;
    private String filePath;
    private Long fileSize;
    private String fileType;
    private String bizType;
    private Long bizId;
    private Long uploaderId;
    private LocalDateTime createTime;
    @TableLogic private Integer deleted;
}
