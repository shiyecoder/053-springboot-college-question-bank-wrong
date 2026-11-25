package com.grad.qb.config;

import com.grad.qb.common.JwtUtil;
import com.grad.qb.common.UserContext;
import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

/** 解析 Authorization: Bearer <token>，写入登录人上下文；请求结束清理 ThreadLocal */
@Component
public class JwtFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    public JwtFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            try {
                Claims c = jwtUtil.parse(header.substring(7));
                Long userId = Long.valueOf(c.getSubject());
                Object dept = c.get("deptId");
                UserContext.set(new UserContext.LoginUser(userId, String.valueOf(c.get("name")),
                        String.valueOf(c.get("role")), dept == null ? null : Long.valueOf(String.valueOf(dept)),
                        String.valueOf(c.get("scope"))));
                SecurityContextHolder.getContext().setAuthentication(new UsernamePasswordAuthenticationToken(
                        userId, null, List.of(new SimpleGrantedAuthority("ROLE_" + c.get("role")))));
            } catch (Exception ignored) {
                UserContext.clear();
                SecurityContextHolder.clearContext();
            }
        }
        try {
            chain.doFilter(request, response);
        } finally {
            UserContext.clear();
            SecurityContextHolder.clearContext();
        }
    }
}
