package com.grad.qb.common;

/** 当前登录人上下文（ThreadLocal）：数据范围 SELF / DEPT / ALL */
public class UserContext {

    public record LoginUser(Long id, String name, String roleCode, Long deptId, String dataScope) {}

    private static final ThreadLocal<LoginUser> HOLDER = new ThreadLocal<>();

    public static void set(LoginUser u) { HOLDER.set(u); }
    public static LoginUser get() { return HOLDER.get(); }

    public static Long id() {
        LoginUser u = HOLDER.get();
        return u == null ? null : u.id();
    }

    public static String name() {
        LoginUser u = HOLDER.get();
        return u == null ? "系统" : u.name();
    }

    public static String role() {
        LoginUser u = HOLDER.get();
        return u == null ? "" : u.roleCode();
    }

    public static String scope() {
        LoginUser u = HOLDER.get();
        return u == null ? "SELF" : u.dataScope();
    }

    public static Long deptId() {
        LoginUser u = HOLDER.get();
        return u == null ? null : u.deptId();
    }

    public static boolean isStudent() { return "STUDENT".equals(role()); }
    public static boolean isAdmin() { return "ADMIN".equals(role()); }
    public static boolean isAuditor() { return "AUDITOR".equals(role()); }

    public static void clear() { HOLDER.remove(); }
}
