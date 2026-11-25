package com.grad.qb.common;

import com.baomidou.mybatisplus.core.metadata.IPage;

import java.util.List;

/** 分页响应体：records + total + page + size + pages（同时提供 list 便于前端表格） */
public class PageResult<T> {
    private List<T> records;
    private List<T> list;
    private long total;
    private long page;
    private long size;
    private long pages;

    public PageResult() {}

    public PageResult(long total, long page, long size, List<T> records) {
        this.records = records;
        this.list = records;
        this.total = total;
        this.page = page;
        this.size = size;
        this.pages = size <= 0 ? 0 : (total + size - 1) / size;
    }

    public static <T> PageResult<T> of(IPage<T> p) {
        return new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords());
    }

    public List<T> getRecords() { return records; }
    public void setRecords(List<T> records) { this.records = records; this.list = records; }
    public List<T> getList() { return list; }
    public void setList(List<T> list) { this.list = list; }
    public long getTotal() { return total; }
    public void setTotal(long total) { this.total = total; }
    public long getPage() { return page; }
    public void setPage(long page) { this.page = page; }
    public long getSize() { return size; }
    public void setSize(long size) { this.size = size; }
    public long getPages() { return pages; }
    public void setPages(long pages) { this.pages = pages; }
}
