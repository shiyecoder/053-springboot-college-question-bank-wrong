package com.grad.qb;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/** 高校智能题库与错题本系统启动类 */
@SpringBootApplication
@EnableScheduling
@MapperScan("com.grad.qb.mapper")
public class QuestionBankApplication {
    public static void main(String[] args) {
        SpringApplication.run(QuestionBankApplication.class, args);
    }
}
