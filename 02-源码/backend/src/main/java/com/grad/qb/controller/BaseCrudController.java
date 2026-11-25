package com.grad.qb.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.qb.common.PageResult;
import com.grad.qb.common.R;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 通用增删改查：分页（关键字 + 状态 + 日期区间 + 任意字段等值）、详情、新增、修改、逻辑删除。
 * 各业务表继承后只需声明表列集合与关键字列，避免重复实现分页与筛选。
 */
public abstract class BaseCrudController<T> {

    protected abstract BaseMapper<T> repo();

    /** 允许作为等值筛选条件的列（下划线命名） */
    protected abstract Set<String> cols();

    /** keyword 模糊匹配列 */
    protected abstract List<String> keywordCols();

    protected String orderCol() {
        return "create_time";
    }

    protected void beforeSave(T body) {}

    protected void beforeUpdate(T body) {}

    @GetMapping("/page")
    public R<PageResult<T>> page(@RequestParam(defaultValue = "1") long page,
                                 @RequestParam(defaultValue = "10") long size,
                                 HttpServletRequest req) {
        if (size > 100) size = 100;
        QueryWrapper<T> w = build(req);
        w.orderByDesc(orderCol()).orderByDesc("id");
        Page<T> p = repo().selectPage(new Page<>(page, size), w);
        return R.ok(PageResult.of(p));
    }

    @GetMapping("/list")
    public R<List<T>> list(HttpServletRequest req) {
        return R.ok(repo().selectList(build(req).
                orderByAsc("id")));
    }

    /** 条件拼装：kw 模糊、create_time 区间、其余列等值 */
    protected QueryWrapper<T> build(HttpServletRequest req) {
        QueryWrapper<T> w = new QueryWrapper<>();
        String kw = req.getParameter("kw");
        if (kw != null && !kw.isBlank() && !keywordCols().isEmpty()) {
            w.and(q -> {
                boolean first = true;
                for (String c : keywordCols()) {
                    if (first) {
                        q.like(c, kw);
                        first = false;
                    } else {
                        q.or().like(c, kw);
                    }
                }
            });
        }
        String st = req.getParameter("startTime");
        String et = req.getParameter("endTime");
        if (st != null && !st.isBlank()) w.ge("create_time", st);
        if (et != null && !et.isBlank()) w.le("create_time", et);
        for (Map.Entry<String, String[]> e : req.getParameterMap().entrySet()) {
            String name = e.getKey();
            if (Set.of("page", "size", "kw", "startTime", "endTime", "_t").contains(name)) continue;
            String val = e.getValue() == null || e.getValue().length == 0 ? null : e.getValue()[0];
            if (val == null || val.isBlank()) continue;
            String col = name.replaceAll("([A-Z])", "_$1").toLowerCase();
            if (cols().contains(col) && !"start_time".equals(col) && !"end_time".equals(col)) {
                w.eq(col, val);
            }
        }
        return w;
    }

    @GetMapping("/{id}")
    public R<T> get(@PathVariable Long id) {
        return R.ok(repo().selectById(id));
    }

    @PostMapping
    public R<T> save(@RequestBody T body) {
        beforeSave(body);
        repo().insert(body);
        return R.ok(body);
    }

    @PutMapping("/{id}")
    public R<T> update(@PathVariable Long id, @RequestBody T body) {
        beforeUpdate(body);
        repo().updateById(body);
        return R.ok(body);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        repo().deleteById(id);
        return R.ok();
    }
}
