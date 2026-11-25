package com.grad.qb.job;

import com.grad.qb.controller.MasteryController;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * 学情诊断每日重算任务。
 * 需求：诊断结果每日凌晨重算一次，重算前后差值超过 10 分的知识点提示教师复核。
 * 重算逻辑与管理员手动入口共用 MasteryController.recomputeAllQuiet，保证两条路径结果一致。
 */
@Component
public class MasteryDailyJob {

    private static final Logger log = LoggerFactory.getLogger(MasteryDailyJob.class);

    private final MasteryController masteryController;

    public MasteryDailyJob(MasteryController masteryController) {
        this.masteryController = masteryController;
    }

    /** 每天 02:00 执行；系统操作员 id 固定为 1（admin） */
    @Scheduled(cron = "0 0 2 * * ?")
    public void dailyRecompute() {
        long begin = System.currentTimeMillis();
        try {
            Map<String, Object> stat = masteryController.recomputeAllQuiet(1L);
            log.info("掌握度每日重算完成：学生 {} 人，诊断 {} 条，变更 {} 条，耗时 {} ms",
                    stat.get("students"), stat.get("rows"), stat.get("changed"),
                    System.currentTimeMillis() - begin);
        } catch (Exception e) {
            log.error("掌握度每日重算失败：{}", e.getMessage(), e);
        }
    }
}
