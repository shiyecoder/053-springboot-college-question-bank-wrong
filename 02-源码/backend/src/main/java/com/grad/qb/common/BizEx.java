package com.grad.qb.common;

/** 业务异常：携带文档定义的错误码 */
public class BizEx extends RuntimeException {
    private final int code;

    public BizEx(int code, String msg) {
        super(msg);
        this.code = code;
    }

    public BizEx(String msg) { this(4000, msg); }

    public int getCode() { return code; }
}
