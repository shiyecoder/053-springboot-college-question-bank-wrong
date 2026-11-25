package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.qb.common.BizEx;
import com.grad.qb.common.PageResult;
import com.grad.qb.common.R;
import com.grad.qb.entity.*;
import com.grad.qb.mapper.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

/** 用户管理：分页、新增（默认密码 123456）、改角色、重置密码 */
@RestController
@RequestMapping("/api/user")
public class UserController {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysUserRoleMapper userRoleMapper;
    private final SysMenuMapper menuMapper;
    private final SysRoleMenuMapper roleMenuMapper;
    private final PasswordEncoder encoder;

    public UserController(SysUserMapper userMapper, SysRoleMapper roleMapper, SysUserRoleMapper userRoleMapper,
                          SysMenuMapper menuMapper, SysRoleMenuMapper roleMenuMapper, PasswordEncoder encoder) {
        this.userMapper = userMapper;
        this.roleMapper = roleMapper;
        this.userRoleMapper = userRoleMapper;
        this.menuMapper = menuMapper;
        this.roleMenuMapper = roleMenuMapper;
        this.encoder = encoder;
    }

    @GetMapping("/page")
    public R<PageResult<Map<String, Object>>> page(@RequestParam(defaultValue = "1") long page,
                                                   @RequestParam(defaultValue = "10") long size,
                                                   @RequestParam(required = false) String kw,
                                                   @RequestParam(required = false) String roleCode,
                                                   @RequestParam(required = false) Integer status,
                                                   @RequestParam(required = false) Long deptId) {
        QueryWrapper<SysUser> w = new QueryWrapper<>();
        if (kw != null && !kw.isBlank()) w.and(q -> q.like("username", kw).or().like("real_name", kw));
        if (status != null) w.eq("status", status);
        if (deptId != null) w.eq("dept_id", deptId);
        if (roleCode != null && !roleCode.isBlank()) {
            List<Long> roleIds = roleMapper.selectList(new QueryWrapper<SysRole>().eq("role_code", roleCode))
                    .stream().map(SysRole::getId).toList();
            if (roleIds.isEmpty()) return R.ok(new PageResult<>(0, page, size, List.of()));
            List<Long> uids = userRoleMapper.selectList(new QueryWrapper<SysUserRole>().in("role_id", roleIds))
                    .stream().map(SysUserRole::getUserId).toList();
            if (uids.isEmpty()) return R.ok(new PageResult<>(0, page, size, List.of()));
            w.in("id", uids);
        }
        w.orderByDesc("id");
        Page<SysUser> p = userMapper.selectPage(new Page<>(page, size), w);
        List<Map<String, Object>> rows = p.getRecords().stream().map(u -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", u.getId());
            m.put("username", u.getUsername());
            m.put("realName", u.getRealName());
            m.put("phone", u.getPhone());
            m.put("email", u.getEmail());
            m.put("avatar", u.getAvatar());
            m.put("deptId", u.getDeptId());
            m.put("className", u.getClassName());
            m.put("status", u.getStatus());
            m.put("lastLogin", u.getLastLogin());
            m.put("createTime", u.getCreateTime());
            SysUserRole ur = userRoleMapper.selectOne(new QueryWrapper<SysUserRole>().eq("user_id", u.getId()));
            SysRole role = ur == null ? null : roleMapper.selectById(ur.getRoleId());
            m.put("roleCode", role == null ? "" : role.getRoleCode());
            m.put("roleName", role == null ? "" : role.getRoleName());
            m.put("dataScope", role == null ? "" : role.getDataScope());
            return m;
        }).collect(Collectors.toList());
        return R.ok(new PageResult<>(p.getTotal(), page, size, rows));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> get(@PathVariable Long id) {
        SysUser u = userMapper.selectById(id);
        if (u == null) throw new BizEx(4000, "用户不存在");
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("user", u);
        SysUserRole ur = userRoleMapper.selectOne(new QueryWrapper<SysUserRole>().eq("user_id", id));
        m.put("roleId", ur == null ? null : ur.getRoleId());
        return R.ok(m);
    }

    @PostMapping
    public R<SysUser> save(@RequestBody Map<String, Object> body) {
        String username = String.valueOf(body.getOrDefault("username", "")).trim();
        if (username.isEmpty()) throw new BizEx(4000, "账号不能为空");
        if (userMapper.selectCount(new QueryWrapper<SysUser>().eq("username", username)) > 0)
            throw new BizEx(4009, "账号已存在");
        SysUser u = new SysUser();
        u.setUsername(username);
        u.setRealName(String.valueOf(body.getOrDefault("realName", username)));
        u.setPhone((String) body.get("phone"));
        u.setEmail((String) body.get("email"));
        u.setAvatar((String) body.get("avatar"));
        u.setClassName((String) body.get("className"));
        u.setStatus(1);
        u.setCreditScore(100);
        u.setPassword(encoder.encode("123456"));
        if (body.get("deptId") != null) u.setDeptId(Long.valueOf(String.valueOf(body.get("deptId"))));
        if (body.get("studentNo") != null) u.setStudentNo(String.valueOf(body.get("studentNo")));
        userMapper.insert(u);
        bindRole(u.getId(), body.get("roleId"));
        u.setPassword(null);
        return R.ok(u);
    }

    @PutMapping("/{id}")
    public R<SysUser> update(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        SysUser u = userMapper.selectById(id);
        if (u == null) throw new BizEx(4000, "用户不存在");
        if (body.get("realName") != null) u.setRealName(String.valueOf(body.get("realName")));
        if (body.get("phone") != null) u.setPhone(String.valueOf(body.get("phone")));
        if (body.get("email") != null) u.setEmail(String.valueOf(body.get("email")));
        if (body.get("avatar") != null) u.setAvatar(String.valueOf(body.get("avatar")));
        if (body.get("className") != null) u.setClassName(String.valueOf(body.get("className")));
        if (body.get("status") != null) u.setStatus(Integer.valueOf(String.valueOf(body.get("status"))));
        if (body.get("deptId") != null) u.setDeptId(Long.valueOf(String.valueOf(body.get("deptId"))));
        userMapper.updateById(u);
        if (body.get("roleId") != null) {
            userRoleMapper.delete(new QueryWrapper<SysUserRole>().eq("user_id", id));
            bindRole(id, body.get("roleId"));
        }
        u.setPassword(null);
        return R.ok(u);
    }

    @PostMapping("/{id}/reset-password")
    public R<Void> reset(@PathVariable Long id) {
        SysUser u = userMapper.selectById(id);
        u.setPassword(encoder.encode("123456"));
        userMapper.updateById(u);
        return R.ok();
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        if (id == 1L) throw new BizEx(4001, "内置管理员不可删除");
        userMapper.deleteById(id);
        return R.ok();
    }

    /** 为角色分配菜单：回显已授权菜单 id */
    @GetMapping("/role/{roleId}/menus")
    public R<List<Long>> roleMenus(@PathVariable Long roleId) {
        return R.ok(roleMenuMapper.selectList(new QueryWrapper<SysRoleMenu>().eq("role_id", roleId))
                .stream().map(SysRoleMenu::getMenuId).toList());
    }

    @PutMapping("/role/{roleId}/menus")
    public R<Void> saveRoleMenus(@PathVariable Long roleId, @RequestBody List<Long> menuIds) {
        roleMenuMapper.delete(new QueryWrapper<SysRoleMenu>().eq("role_id", roleId));
        for (Long mid : menuIds) {
            SysRoleMenu rm = new SysRoleMenu();
            rm.setRoleId(roleId);
            rm.setMenuId(mid);
            roleMenuMapper.insert(rm);
        }
        return R.ok();
    }

    private void bindRole(Long userId, Object roleId) {
        SysUserRole ur = new SysUserRole();
        ur.setUserId(userId);
        ur.setRoleId(roleId == null ? 5L : Long.valueOf(String.valueOf(roleId)));
        userRoleMapper.insert(ur);
    }
}
