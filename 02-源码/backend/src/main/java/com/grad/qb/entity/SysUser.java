package com.grad.qb.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/** sys_user 实体，字段与 sql/init.sql 一一对应 */
@Data
@TableName("sys_user")
public class SysUser {
    @TableId(type = IdType.AUTO) private Long id;
    private String username;
    private String password;
    private String realName;
    private String phone;
    private String email;
    private String avatar;
    private String studentNo;
    private Long deptId;
    private String className;
    private Integer status;
    private Integer creditScore;
    private LocalDateTime lastLogin;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    @TableLogic private Integer deleted;
}
