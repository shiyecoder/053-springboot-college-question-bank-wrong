package com.grad.qb.common;

import java.util.UUID;

/** 统一响应：code=0 成功，非 0 为业务错误码（对齐需求文档 7.6） */
public class R<T> {
    private int code;
    private String msg;
    private T data;
    private String requestId;

    public R() {}

    public R(int code, String msg, T data) {
        this.code = code;
        this.msg = msg;
        this.data = data;
        this.requestId = UUID.randomUUID().toString().substring(0, 8);
    }

    public static <T> R<T> ok(T data) { return new R<>(0, "success", data); }
    public static <T> R<T> ok() { return new R<>(0, "success", null); }
    public static <T> R<T> fail(int code, String msg) { return new R<>(code, msg, null); }
    public static <T> R<T> fail(String msg) { return new R<>(5000, msg, null); }

    public int getCode() { return code; }
    public void setCode(int code) { this.code = code; }
    public String getMsg() { return msg; }
    public void setMsg(String msg) { this.msg = msg; }
    public T getData() { return data; }
    public void setData(T data) { this.data = data; }
    public String getRequestId() { return requestId; }
    public void setRequestId(String requestId) { this.requestId = requestId; }
}
