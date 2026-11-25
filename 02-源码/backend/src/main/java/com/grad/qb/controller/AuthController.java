package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.grad.qb.common.BizEx;
import com.grad.qb.common.JwtUtil;
import com.grad.qb.common.R;
import com.grad.qb.common.UserContext;
import com.grad.qb.entity.*;
import com.grad.qb.mapper.*;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;

/** 登录、当前用户、菜单（按角色动态获取）、修改密码 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysUserRoleMapper userRoleMapper;
    private final SysMenuMapper menuMapper;
    private final SysRoleMenuMapper roleMenuMapper;
    private final SysMessageMapper messageMapper;
    private final PasswordEncoder encoder;
    private final JwtUtil jwtUtil;

    public AuthController(SysUserMapper userMapper, SysRoleMapper roleMapper, SysUserRoleMapper userRoleMapper,
                          SysMenuMapper menuMapper, SysRoleMenuMapper roleMenuMapper,
                          SysMessageMapper messageMapper, PasswordEncoder encoder, JwtUtil jwtUtil) {
        this.userMapper = userMapper;
        this.roleMapper = roleMapper;
        this.userRoleMapper = userRoleMapper;
        this.menuMapper = menuMapper;
        this.roleMenuMapper = roleMenuMapper;
        this.messageMapper = messageMapper;
        this.encoder = encoder;
        this.jwtUtil = jwtUtil;
    }

    /** 登录：BCrypt 校验，签发 JWT，回写最近登录时间 */
    @PostMapping("/login")
    public R<Map<String, Object>> login(@RequestBody Map<String, String> body) {
        String username = body.get("username");
        String password = body.get("password");
        if (username == null || password == null) throw new BizEx(4000, "请输入账号和密码");
        SysUser u = userMapper.selectOne(new QueryWrapper<SysUser>().eq("username", username.trim()));
        if (u == null) throw new BizEx(4000, "账号或密码错误");
        if (u.getStatus() != null && u.getStatus() == 0) throw new BizEx(4001, "账号已停用，请联系管理员");
        if (!encoder.matches(password, u.getPassword())) throw new BizEx(4000, "账号或密码错误");
        SysRole role = currentRole(u.getId());
        Map<String, Object> claims = new HashMap<>();
        claims.put("name", u.getRealName());
        claims.put("role", role == null ? "STUDENT" : role.getRoleCode());
        claims.put("deptId", u.getDeptId());
        claims.put("scope", role == null ? "SELF" : role.getDataScope());
        String token = jwtUtil.create(claims, u.getId());
        u.setLastLogin(LocalDateTime.now());
        userMapper.updateById(u);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("token", token);
        data.put("user", safeUser(u, role));
        data.put("menus", menusOf(role == null ? null : role.getId()));
        return R.ok(data);
    }

    @GetMapping("/info")
    public R<Map<String, Object>> info() {
        Long uid = UserContext.id();
        SysUser u = userMapper.selectById(uid);
        if (u == null) throw new BizEx(4010, "登录已失效");
        SysRole role = currentRole(uid);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("user", safeUser(u, role));
        data.put("menus", menusOf(role == null ? null : role.getId()));
        data.put("unread", messageMapper.selectCount(new QueryWrapper<SysMessage>()
                .eq("receiver_id", uid).eq("read_flag", 0)));
        return R.ok(data);
    }

    @GetMapping("/menus")
    public R<List<Map<String, Object>>> menus() {
        SysRole role = currentRole(UserContext.id());
        return R.ok(menusOf(role == null ? null : role.getId()));
    }

    @PostMapping("/password")
    public R<Void> password(@RequestBody Map<String, String> body) {
        Long uid = UserContext.id();
        SysUser u = userMapper.selectById(uid);
        String oldPwd = body.get("oldPassword");
        String newPwd = body.get("newPassword");
        if (oldPwd == null || newPwd == null || newPwd.length() < 6) throw new BizEx(4000, "新密码不少于 6 位");
        if (!encoder.matches(oldPwd, u.getPassword())) throw new BizEx(4000, "原密码不正确");
        u.setPassword(encoder.encode(newPwd));
        userMapper.updateById(u);
        return R.ok();
    }

    private SysRole currentRole(Long userId) {
        List<SysUserRole> urs = userRoleMapper.selectList(new QueryWrapper<SysUserRole>().eq("user_id", userId));
        if (urs.isEmpty()) return null;
        return roleMapper.selectById(urs.get(0).getRoleId());
    }

    private Map<String, Object> safeUser(SysUser u, SysRole role) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", u.getId());
        m.put("username", u.getUsername());
        m.put("realName", u.getRealName());
        m.put("avatar", u.getAvatar());
        m.put("phone", u.getPhone());
        m.put("email", u.getEmail());
        m.put("studentNo", u.getStudentNo());
        m.put("className", u.getClassName());
        m.put("deptId", u.getDeptId());
        m.put("roleCode", role == null ? "STUDENT" : role.getRoleCode());
        m.put("roleName", role == null ? "学生" : role.getRoleName());
        m.put("dataScope", role == null ? "SELF" : role.getDataScope());
        return m;
    }

    /** 菜单按角色权限动态获取：只返回目录与菜单，按钮走 perms 校验 */
    private List<Map<String, Object>> menusOf(Long roleId) {
        List<SysMenu> all;
        if (roleId == null) {
            all = List.of();
        } else if (roleId == 1L) {
            all = menuMapper.selectList(new QueryWrapper<SysMenu>().orderByAsc("sort_no"));
        } else {
            List<Long> ids = roleMenuMapper.selectList(new QueryWrapper<SysRoleMenu>().eq("role_id", roleId))
                    .stream().map(SysRoleMenu::getMenuId).toList();
            if (ids.isEmpty()) return List.of();
            all = menuMapper.selectList(new QueryWrapper<SysMenu>().in("id", ids).orderByAsc("sort_no"));
        }
        List<Map<String, Object>> roots = new ArrayList<>();
        for (SysMenu m : all) {
            if (m.getParentId() == null || m.getParentId() == 0) {
                Map<String, Object> node = toNode(m);
                node.put("children", children(all, m.getId()));
                roots.add(node);
            }
        }
        return roots;
    }

    private List<Map<String, Object>> children(List<SysMenu> all, Long pid) {
        List<Map<String, Object>> list = new ArrayList<>();
        for (SysMenu m : all) {
            if (pid.equals(m.getParentId())) {
                Map<String, Object> node = toNode(m);
                node.put("children", children(all, m.getId()));
                list.add(node);
            }
        }
        return list;
    }

    private Map<String, Object> toNode(SysMenu m) {
        Map<String, Object> n = new LinkedHashMap<>();
        n.put("id", m.getId());
        n.put("name", m.getMenuName());
        n.put("path", m.getPath());
        n.put("component", m.getComponent());
        n.put("perms", m.getPerms());
        n.put("type", m.getMenuType());
        n.put("icon", m.getIcon());
        return n;
    }
}
