package com.grad.qb.controller;

import com.grad.qb.common.R;
import com.grad.qb.common.UserContext;
import com.grad.qb.entity.SysUser;
import com.grad.qb.mapper.SysUserMapper;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 个人信息：改资料、上传头像（头像路径由上传接口返回，前端右上角同步） */
@RestController
@RequestMapping("/api/profile")
public class ProfileController {

    private final SysUserMapper mapper;

    public ProfileController(SysUserMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping
    public R<SysUser> get() {
        SysUser u = mapper.selectById(UserContext.id());
        if (u != null) u.setPassword(null);
        return R.ok(u);
    }

    @PutMapping
    public R<SysUser> update(@RequestBody Map<String, Object> body) {
        SysUser u = mapper.selectById(UserContext.id());
        if (body.get("realName") != null) u.setRealName(String.valueOf(body.get("realName")));
        if (body.get("phone") != null) u.setPhone(String.valueOf(body.get("phone")));
        if (body.get("email") != null) u.setEmail(String.valueOf(body.get("email")));
        if (body.get("avatar") != null) u.setAvatar(String.valueOf(body.get("avatar")));
        mapper.updateById(u);
        u.setPassword(null);
        return R.ok(u);
    }
}
