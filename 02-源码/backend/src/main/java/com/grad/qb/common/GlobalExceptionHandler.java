package com.grad.qb.common;

import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** 全局异常：业务异常按码返回，校验异常返回 4000 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BizEx.class)
    public R<Void> biz(BizEx e) {
        return R.fail(e.getCode(), e.getMessage());
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class})
    public R<Void> valid(Exception e) {
        String msg = "参数校验失败";
        if (e instanceof MethodArgumentNotValidException m && m.getBindingResult().getFieldError() != null) {
            msg = m.getBindingResult().getFieldError().getDefaultMessage();
        }
        return R.fail(4000, msg);
    }

    @ExceptionHandler(Exception.class)
    public R<Void> other(Exception e) {
        e.printStackTrace();
        return R.fail(5000, "服务器异常：" + e.getMessage());
    }
}
