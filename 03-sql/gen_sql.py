#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 new_053 初始化脚本：建库 + 26 张表 + 全量测试数据（跨 6 个月，覆盖全部状态）"""
import datetime as dt
import pathlib

def esc(v):
    """SQL 单引号转义，避免题干里的导数符号打断语句"""
    return str(v).replace("'", "''")


PWD = "$2b$10$.JBgiudHQ2HQ4GGXoOt2RuKsEuMqq8dlQsrmTwn/Uyg2SWyOnlHxW"  # 123456
BASE = dt.datetime(2026, 11, 1, 7, 0, 0)
OUT = pathlib.Path(__file__).parent / "init.sql"

out = []
w = out.append

w("""-- ============================================================
-- 高校智能题库与错题本系统 new_053 初始化脚本
-- MySQL 8.0 / utf8mb4 / InnoDB，可在空库一次性执行
-- 默认账号：admin、auditor、teacher01、secretary、2023010101，密码均 123456
-- ============================================================
DROP DATABASE IF EXISTS `new_053`;
CREATE DATABASE `new_053` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `new_053`;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
""")

# ---------------- 业务表 ----------------
w("""
-- 1. subject 学科
CREATE TABLE `subject` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `subject_no` varchar(20) NOT NULL COMMENT '规则 XK+3位序号，全局唯一',
  `subject_name` varchar(50) NOT NULL COMMENT '如高等数学、数据结构，全局不可重名',
  `edu_level` varchar(20) NOT NULL DEFAULT '本科' COMMENT '中职/高职/本科/研究生',
  `dept_id` bigint NOT NULL COMMENT '关联 sys_dept.id',
  `owner_id` bigint NOT NULL COMMENT '关联 sys_user.id，负责题目终审',
  `question_count` int NOT NULL DEFAULT 0 COMMENT '由题目表统计，审核入库加1，停用减1',
  `pass_rate` decimal(5,2) NOT NULL DEFAULT 60.00 COMMENT '0至100，用于掌握度分档基准',
  `sort_no` int NOT NULL DEFAULT 0 COMMENT '值越小越靠前',
  `status` tinyint NOT NULL DEFAULT 1 COMMENT '1启用 0停用，停用后不可组卷',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_subject_no` (`subject_no`),
  UNIQUE KEY `uk_subject_name` (`subject_name`),
  KEY `idx_status_sort` (`status`, `sort_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学科';

-- 2. knowledge_point 知识点
CREATE TABLE `knowledge_point` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `kp_no` varchar(30) NOT NULL COMMENT '规则 ZS+学科码+4位序号，同学科内唯一',
  `subject_id` bigint NOT NULL COMMENT '关联 subject.id',
  `parent_id` bigint NOT NULL DEFAULT 0 COMMENT '0表示一级知识点，最多三级',
  `kp_name` varchar(80) NOT NULL COMMENT '同一父级下不可重名',
  `kp_level` tinyint NOT NULL DEFAULT 1 COMMENT '1至3，由 parent_id 推导并校验一致',
  `exam_weight` decimal(5,2) NOT NULL DEFAULT 5.00 COMMENT '0至100，同学科一级节点合计不超过100',
  `question_count` int NOT NULL DEFAULT 0 COMMENT '仅统计已入库题目',
  `mastery_threshold` decimal(5,2) NOT NULL DEFAULT 80.00 COMMENT '0至100，达到该正确率视为已掌握',
  `status` tinyint NOT NULL DEFAULT 1 COMMENT '1启用 0停用',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_kp_no` (`kp_no`),
  KEY `idx_subject_parent` (`subject_id`, `parent_id`),
  KEY `idx_subject_weight` (`subject_id`, `exam_weight`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点';

-- 3. question 题目
CREATE TABLE `question` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `question_no` varchar(32) NOT NULL COMMENT '规则 TM+学科码+6位序号，全局唯一',
  `subject_id` bigint NOT NULL COMMENT '关联 subject.id',
  `knowledge_point_id` bigint NOT NULL COMMENT '关联 knowledge_point.id，须属于同学科',
  `question_type` varchar(20) NOT NULL DEFAULT '单选' COMMENT '单选/多选/判断/填空/简答/计算',
  `stem` text NOT NULL COMMENT '不少于8字，公式用文字描述，禁止只放图片',
  `answer` varchar(1000) NOT NULL COMMENT '单选填A，多选按字母升序逗号分隔',
  `analysis` text DEFAULT NULL COMMENT '入库时必填，至少20字说明解题步骤',
  `difficulty` decimal(3,2) NOT NULL DEFAULT 0.60 COMMENT '0.10至1.00，由历史正确率动态校准',
  `score` decimal(5,1) NOT NULL DEFAULT 5.0 COMMENT '1至50，同一试卷内合计等于总分',
  `source_type` varchar(20) NOT NULL DEFAULT '自建' COMMENT '自建/真题/教材/引进',
  `correct_rate` decimal(5,2) NOT NULL DEFAULT 0.00 COMMENT '0至100，作答次数为0时页面显示未测',
  `status` varchar(20) NOT NULL DEFAULT '待审核' COMMENT '草稿/待审核/已入库/已停用/已退回',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_question_no` (`question_no`),
  KEY `idx_kp_status` (`knowledge_point_id`, `status`),
  KEY `idx_subject_type` (`subject_id`, `question_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目';

-- 4. question_option 题目选项
CREATE TABLE `question_option` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `question_id` bigint NOT NULL COMMENT '关联 question.id，仅选择题生成选项',
  `option_label` varchar(4) NOT NULL COMMENT 'A至H，同一题目内唯一',
  `option_content` varchar(500) NOT NULL COMMENT '最多200字，不允许为空',
  `is_correct` tinyint NOT NULL DEFAULT 0 COMMENT '1正确 0错误，单选题正确项必须有且只有1个',
  `sort_no` int NOT NULL DEFAULT 1 COMMENT '按A至H顺序展示',
  `image_url` varchar(255) DEFAULT NULL COMMENT '公式或图形选项使用，最多1张',
  `distractor_note` varchar(200) DEFAULT NULL COMMENT '标注该错误选项对应的典型误区',
  `chosen_count` int NOT NULL DEFAULT 0 COMMENT '统计各选项被选比例，用于难度校准',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_question_label` (`question_id`, `option_label`),
  KEY `idx_question_sort` (`question_id`, `sort_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目选项';

-- 5. paper 试卷
CREATE TABLE `paper` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `paper_no` varchar(32) NOT NULL COMMENT '规则 SJ+yyMMdd+4位序号，全局唯一',
  `paper_name` varchar(100) NOT NULL COMMENT '2至60字，同学科内不可重名',
  `subject_id` bigint NOT NULL COMMENT '关联 subject.id',
  `build_mode` varchar(20) NOT NULL DEFAULT '手动' COMMENT '手动/随机/错题重练',
  `question_count` int NOT NULL DEFAULT 0 COMMENT '5至100，与明细条数一致',
  `total_score` decimal(5,1) NOT NULL DEFAULT 100.0 COMMENT '题目分值合计必须等于总分',
  `duration_min` int NOT NULL DEFAULT 60 COMMENT '10至240分钟，超过2倍自动交卷',
  `difficulty_avg` decimal(3,2) NOT NULL DEFAULT 0.60 COMMENT '0.10至1.00，由明细题目加权计算',
  `random_rule` varchar(500) DEFAULT NULL COMMENT '随机卷必填，按知识点与题数、难度区间描述',
  `creator_id` bigint NOT NULL COMMENT '关联 sys_user.id',
  `status` varchar(20) NOT NULL DEFAULT '草稿' COMMENT '草稿/待审核/已发布/使用中/已归档/已驳回',
  `reject_reason` varchar(200) DEFAULT NULL COMMENT '驳回时必填并通知创建人',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_paper_no` (`paper_no`),
  KEY `idx_subject_status` (`subject_id`, `status`),
  KEY `idx_creator_status` (`creator_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='试卷';

-- 6. paper_question 试卷题目明细
CREATE TABLE `paper_question` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `paper_id` bigint NOT NULL COMMENT '关联 paper.id',
  `question_id` bigint NOT NULL COMMENT '关联 question.id，同一试卷不可重复',
  `section_no` int NOT NULL DEFAULT 1 COMMENT '1至10，按题型划分大题',
  `sort_no` int NOT NULL DEFAULT 1 COMMENT '同大题内连续编号',
  `score` decimal(5,1) NOT NULL DEFAULT 5.0 COMMENT '可覆盖题库默认分值，合计等于试卷总分',
  `question_type` varchar(20) NOT NULL COMMENT '组卷时写入，防止题库改动影响历史卷',
  `knowledge_point_id` bigint NOT NULL COMMENT '组卷时写入，用于知识点覆盖度统计',
  `stem_snapshot` text NOT NULL COMMENT '发布时冻结，学生端展示该字段',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_paper_question` (`paper_id`, `question_id`),
  KEY `idx_paper_section` (`paper_id`, `section_no`, `sort_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='试卷题目明细';

-- 7. practice_record 练习记录
CREATE TABLE `practice_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `record_no` varchar(32) NOT NULL COMMENT '规则 LX+yyMMdd+6位序号，全局唯一',
  `paper_id` bigint DEFAULT NULL COMMENT '关联 paper.id，错题重练时为空',
  `student_id` bigint NOT NULL COMMENT '关联 sys_user.id',
  `practice_type` varchar(20) NOT NULL DEFAULT '试卷练习' COMMENT '试卷练习/知识点练习/错题重练',
  `start_time` datetime NOT NULL COMMENT '进入答题页时写入',
  `submit_time` datetime DEFAULT NULL COMMENT '超过建议时长2倍由系统自动交卷',
  `used_seconds` int NOT NULL DEFAULT 0 COMMENT '交卷时间减开始时间，上限86400',
  `question_count` int NOT NULL DEFAULT 0 COMMENT '本次练习实际题目数',
  `correct_count` int NOT NULL DEFAULT 0 COMMENT '自动判分结果，不得超过总题数',
  `got_score` decimal(5,1) NOT NULL DEFAULT 0.0 COMMENT '客观题自动计分，简答按关键词命中给分',
  `status` varchar(20) NOT NULL DEFAULT '进行中' COMMENT '进行中/已交卷/已批阅/已作废',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_record_no` (`record_no`),
  KEY `idx_student_start` (`student_id`, `start_time`),
  KEY `idx_paper_status` (`paper_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='练习记录';

-- 8. wrong_book 错题本
CREATE TABLE `wrong_book` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `student_id` bigint NOT NULL COMMENT '关联 sys_user.id，同一学生同一题目仅一条',
  `question_id` bigint NOT NULL COMMENT '关联 question.id',
  `subject_id` bigint NOT NULL COMMENT '冗余学科字段，便于按学科筛选',
  `knowledge_point_id` bigint NOT NULL COMMENT '关联 knowledge_point.id，用于薄弱诊断',
  `wrong_count` int NOT NULL DEFAULT 1 COMMENT '每答错一次加1，答对不清零',
  `last_wrong_time` datetime NOT NULL COMMENT '取最近一次答错时间',
  `last_answer` varchar(500) DEFAULT NULL COMMENT '保存学生最近一次作答内容',
  `correct_streak` tinyint NOT NULL DEFAULT 0 COMMENT '连续答对2次可转为已掌握',
  `source_record_id` bigint DEFAULT NULL COMMENT '关联 practice_record.id',
  `status` varchar(20) NOT NULL DEFAULT '未掌握' COMMENT '未掌握/复习中/已掌握/已移除',
  `note` varchar(200) DEFAULT NULL COMMENT '学生自填错因，最多100字',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `update_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时自动刷新',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_student_question` (`student_id`, `question_id`),
  KEY `idx_student_status` (`student_id`, `status`),
  KEY `idx_kp_student` (`knowledge_point_id`, `student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='错题本';

-- 9. practice_answer 作答明细（判分与掌握度诊断的样本来源）
CREATE TABLE `practice_answer` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `record_id` bigint NOT NULL COMMENT '关联 practice_record.id',
  `question_id` bigint NOT NULL COMMENT '关联 question.id',
  `student_id` bigint NOT NULL COMMENT '关联 sys_user.id，冗余便于按学生统计',
  `knowledge_point_id` bigint NOT NULL COMMENT '知识点快照，诊断按此汇总',
  `user_answer` varchar(1000) DEFAULT NULL COMMENT '学生作答内容',
  `is_correct` tinyint NOT NULL DEFAULT 0 COMMENT '1正确 0错误 2部分得分',
  `got_score` decimal(5,1) NOT NULL DEFAULT 0.0 COMMENT '本题得分',
  `full_score` decimal(5,1) NOT NULL DEFAULT 0.0 COMMENT '本题满分',
  `used_seconds` int NOT NULL DEFAULT 0 COMMENT '本题作答秒数，用于耗时因子',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  KEY `idx_record` (`record_id`),
  KEY `idx_student_kp` (`student_id`, `knowledge_point_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作答明细';

-- 10. mastery_rule 掌握度规则（创新点：规则可配置、版本化）
CREATE TABLE `mastery_rule` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `rule_name` varchar(60) NOT NULL COMMENT '规则名称',
  `rule_version` varchar(20) NOT NULL COMMENT '版本号，如 v3',
  `w_accuracy` decimal(5,2) NOT NULL DEFAULT 40.00 COMMENT '近30天正确率权重',
  `w_time` decimal(5,2) NOT NULL DEFAULT 15.00 COMMENT '平均耗时比权重',
  `w_redo` decimal(5,2) NOT NULL DEFAULT 20.00 COMMENT '错题重做表现权重',
  `w_weight` decimal(5,2) NOT NULL DEFAULT 15.00 COMMENT '考纲权重因子权重',
  `w_review` decimal(5,2) NOT NULL DEFAULT 10.00 COMMENT '复习及时率权重',
  `pass_level` decimal(5,2) NOT NULL DEFAULT 85.00 COMMENT '已掌握分档线',
  `good_level` decimal(5,2) NOT NULL DEFAULT 70.00 COMMENT '基本掌握分档线',
  `weak_level` decimal(5,2) NOT NULL DEFAULT 50.00 COMMENT '薄弱分档线',
  `effect_time` datetime NOT NULL COMMENT '生效时间',
  `status` varchar(20) NOT NULL DEFAULT '生效中' COMMENT '生效中/已归档',
  `remark` varchar(200) DEFAULT NULL COMMENT '变更说明',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_rule_version` (`rule_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='掌握度规则';

-- 11. mastery_result 掌握度计算结果（留痕：输入快照 + 五因子得分 + 人工修正）
CREATE TABLE `mastery_result` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `student_id` bigint NOT NULL COMMENT '关联 sys_user.id',
  `subject_id` bigint NOT NULL COMMENT '关联 subject.id',
  `knowledge_point_id` bigint NOT NULL COMMENT '关联 knowledge_point.id',
  `rule_id` bigint NOT NULL COMMENT '关联 mastery_rule.id，保证结果可追溯',
  `rule_version` varchar(20) NOT NULL COMMENT '计算时所用规则版本',
  `accuracy_score` decimal(5,2) NOT NULL DEFAULT 0.00 COMMENT '正确率因子归一化得分',
  `time_score` decimal(5,2) NOT NULL DEFAULT 0.00 COMMENT '耗时因子归一化得分',
  `redo_score` decimal(5,2) NOT NULL DEFAULT 0.00 COMMENT '重做表现因子得分',
  `weight_score` decimal(5,2) NOT NULL DEFAULT 0.00 COMMENT '考纲权重因子得分',
  `review_score` decimal(5,2) NOT NULL DEFAULT 0.00 COMMENT '复习及时率因子得分',
  `total_score` decimal(5,2) NOT NULL DEFAULT 0.00 COMMENT '加权总分',
  `level` varchar(20) NOT NULL COMMENT '已掌握/基本掌握/薄弱/严重薄弱/未测',
  `sample_count` int NOT NULL DEFAULT 0 COMMENT '样本量（作答次数），少于5标注数据不足',
  `input_snapshot` text COMMENT '输入快照 JSON，重算可复现',
  `manual_level` varchar(20) DEFAULT NULL COMMENT '人工修正后的等级，原始 level 保留',
  `manual_reason` varchar(200) DEFAULT NULL COMMENT '修正原因，不少于5字',
  `manual_by` bigint DEFAULT NULL COMMENT '修正人',
  `manual_time` datetime DEFAULT NULL COMMENT '修正时间',
  `calc_time` datetime NOT NULL COMMENT '计算时间',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁，更新时校验并加1',
  PRIMARY KEY (`id`),
  KEY `idx_student_kp` (`student_id`, `knowledge_point_id`),
  KEY `idx_subject_level` (`subject_id`, `level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='掌握度计算结果';

-- 12. wrong_review_plan 错题复习计划（1/3/7 天）
CREATE TABLE `wrong_review_plan` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `wrong_id` bigint NOT NULL COMMENT '关联 wrong_book.id',
  `student_id` bigint NOT NULL COMMENT '关联 sys_user.id',
  `plan_day` tinyint NOT NULL COMMENT '1/3/7 天节点',
  `plan_date` date NOT NULL COMMENT '计划复习日期',
  `done_flag` tinyint NOT NULL DEFAULT 0 COMMENT '1已完成 0未完成',
  `done_time` datetime DEFAULT NULL COMMENT '完成时间',
  `result` varchar(20) DEFAULT NULL COMMENT '重练结果：答对/答错',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  PRIMARY KEY (`id`),
  KEY `idx_wrong` (`wrong_id`),
  KEY `idx_student_date` (`student_id`, `plan_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='错题复习计划';

-- 13. question_audit 题目审核流水
CREATE TABLE `question_audit` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `question_id` bigint NOT NULL COMMENT '关联 question.id',
  `auditor_id` bigint NOT NULL COMMENT '审核人，不得为创建人',
  `audit_result` varchar(20) NOT NULL COMMENT '通过/退回',
  `reason_type` varchar(30) DEFAULT NULL COMMENT '退回原因分类',
  `reason` varchar(200) DEFAULT NULL COMMENT '退回说明，5至200字',
  `submit_times` int NOT NULL DEFAULT 1 COMMENT '第几次提交',
  `audit_time` datetime NOT NULL COMMENT '审核时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  PRIMARY KEY (`id`),
  KEY `idx_question` (`question_id`),
  KEY `idx_auditor` (`auditor_id`, `audit_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目审核流水';

-- 14. import_task 批量导入任务
CREATE TABLE `import_task` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `file_name` varchar(200) NOT NULL COMMENT '上传的 Excel 文件名',
  `subject_id` bigint NOT NULL COMMENT '导入目标学科',
  `total_rows` int NOT NULL DEFAULT 0 COMMENT '总行数',
  `success_rows` int NOT NULL DEFAULT 0 COMMENT '成功条数',
  `fail_rows` int NOT NULL DEFAULT 0 COMMENT '失败条数',
  `fail_detail` text COMMENT '失败行明细（行号+原因）',
  `status` varchar(20) NOT NULL DEFAULT '待执行' COMMENT '待执行/执行中/已完成/部分失败/已失败',
  `operator_id` bigint NOT NULL COMMENT '发起人',
  `finish_time` datetime DEFAULT NULL COMMENT '完成时间',
  `create_by` bigint DEFAULT NULL COMMENT '关联 sys_user.id',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  `deleted` tinyint NOT NULL DEFAULT 0 COMMENT '0正常 1删除，查询默认过滤',
  PRIMARY KEY (`id`),
  KEY `idx_operator` (`operator_id`, `create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='批量导入任务';
""")

# ---------------- 通用表 ----------------
w("""
-- 15. sys_dept 部门
CREATE TABLE `sys_dept` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `parent_id` bigint NOT NULL DEFAULT 0,
  `dept_name` varchar(60) NOT NULL,
  `leader` varchar(30) DEFAULT NULL,
  `sort_no` int NOT NULL DEFAULT 0,
  `status` tinyint NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门';

-- 16. sys_user 用户
CREATE TABLE `sys_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(40) NOT NULL,
  `password` varchar(100) NOT NULL COMMENT 'BCrypt',
  `real_name` varchar(40) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(80) DEFAULT NULL,
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像相对路径',
  `student_no` varchar(30) DEFAULT NULL COMMENT '学号/工号',
  `dept_id` bigint DEFAULT NULL,
  `class_name` varchar(40) DEFAULT NULL COMMENT '班级',
  `status` tinyint NOT NULL DEFAULT 1,
  `credit_score` int NOT NULL DEFAULT 100 COMMENT '信用分',
  `last_login` datetime DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户';

-- 17. sys_role 角色
CREATE TABLE `sys_role` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role_name` varchar(40) NOT NULL,
  `role_code` varchar(40) NOT NULL,
  `data_scope` varchar(20) NOT NULL DEFAULT 'SELF' COMMENT 'SELF/DEPT/ALL',
  `remark` varchar(120) DEFAULT NULL,
  `status` tinyint NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色';

-- 18. sys_user_role 用户角色
CREATE TABLE `sys_user_role` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色';

-- 19. sys_menu 菜单
CREATE TABLE `sys_menu` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `parent_id` bigint NOT NULL DEFAULT 0,
  `menu_name` varchar(40) NOT NULL,
  `path` varchar(80) DEFAULT NULL,
  `component` varchar(80) DEFAULT NULL,
  `perms` varchar(80) DEFAULT NULL,
  `menu_type` char(1) NOT NULL DEFAULT 'M' COMMENT 'D目录 M菜单 B按钮',
  `icon` varchar(40) DEFAULT NULL,
  `sort_no` int NOT NULL DEFAULT 0,
  `visible` tinyint NOT NULL DEFAULT 1,
  `status` tinyint NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_parent` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜单权限';

-- 20. sys_role_menu 角色菜单
CREATE TABLE `sys_role_menu` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `role_id` bigint NOT NULL,
  `menu_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_role` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单';

-- 21. sys_dict_type 字典类型
CREATE TABLE `sys_dict_type` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `dict_name` varchar(60) NOT NULL,
  `dict_type` varchar(60) NOT NULL,
  `status` tinyint NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dict_type` (`dict_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字典类型';

-- 22. sys_dict_data 字典数据
CREATE TABLE `sys_dict_data` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `dict_type` varchar(60) NOT NULL,
  `dict_label` varchar(60) NOT NULL,
  `dict_value` varchar(60) NOT NULL,
  `sort_no` int NOT NULL DEFAULT 0,
  `status` tinyint NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `idx_type` (`dict_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字典数据';

-- 23. sys_file 文件
CREATE TABLE `sys_file` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_name` varchar(200) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `file_size` bigint NOT NULL DEFAULT 0,
  `file_type` varchar(30) DEFAULT NULL,
  `biz_type` varchar(40) DEFAULT NULL,
  `biz_id` bigint DEFAULT NULL,
  `uploader_id` bigint DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文件';

-- 24. sys_notice 公告
CREATE TABLE `sys_notice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(120) NOT NULL,
  `content` text,
  `publish_time` datetime DEFAULT NULL,
  `status` tinyint NOT NULL DEFAULT 1,
  `create_by` bigint DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公告';

-- 25. sys_message 站内消息
CREATE TABLE `sys_message` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `receiver_id` bigint NOT NULL,
  `title` varchar(120) NOT NULL,
  `content` varchar(500) DEFAULT NULL,
  `biz_type` varchar(40) DEFAULT NULL,
  `biz_id` bigint DEFAULT NULL,
  `read_flag` tinyint NOT NULL DEFAULT 0,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` tinyint NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_receiver` (`receiver_id`, `read_flag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站内消息';

-- 26. sys_oper_log 操作日志
CREATE TABLE `sys_oper_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `module` varchar(60) NOT NULL,
  `oper_type` varchar(30) NOT NULL,
  `biz_no` varchar(40) DEFAULT NULL,
  `content` varchar(500) DEFAULT NULL,
  `oper_id` bigint DEFAULT NULL,
  `oper_name` varchar(40) DEFAULT NULL,
  `oper_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ip` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_time` (`oper_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志';
""")

# ---------------- 种子数据 ----------------
w("\n-- ============ 基础数据 ============")
depts = [(1, 0, "教务处", "赵敏"), (2, 0, "数学教研室", "李静"), (3, 0, "计算机学院", "王振"),
         (4, 0, "物理教研室", "周敏")]
w("INSERT INTO `sys_dept`(`id`,`parent_id`,`dept_name`,`leader`,`sort_no`) VALUES " +
  ",".join(f"({a},{b},'{c}','{d}',{a})" for a, b, c, d in depts) + ";")

roles = [(1, "系统管理员", "ADMIN", "ALL", "全部数据"),
         (2, "教研员", "AUDITOR", "DEPT", "本部门数据"),
         (3, "任课教师", "TEACHER", "DEPT", "本人所带班级"),
         (4, "院系教学秘书", "SECRETARY", "ALL", "全院统计"),
         (5, "学生", "STUDENT", "SELF", "仅本人数据")]
w("INSERT INTO `sys_role`(`id`,`role_name`,`role_code`,`data_scope`,`remark`) VALUES " +
  ",".join(f"({a},'{b}','{c}','{d}','{e}')" for a, b, c, d, e in roles) + ";")

# 用户：id 1-6 教职工，11-16 学生
users = [(1, "admin", "系统管理员", 1, None, "教务处", None),
         (2, "auditor", "李静", 2, None, "数学教研室", None),
         (3, "auditor2", "陈文博", 2, None, "计算机学院", None),
         (4, "teacher01", "王振", 3, None, "计算机学院", None),
         (5, "teacher02", "周敏", 3, None, "物理教研室", None),
         (6, "secretary", "赵敏", 4, None, "教务处", None),
         (7, "secretary2", "孙倩", 4, None, "教务处", None)]
students = [("2023010101", "陈皓", "计算机 2301"), ("2023010107", "吴思远", "计算机 2301"),
            ("2023010108", "张梓睿", "计算机 2301"), ("2023010119", "何书瑶", "计算机 2301"),
            ("2023010122", "周雨桐", "计算机 2302"), ("2023010133", "刘泽宇", "计算机 2302"),
            ("2023010145", "林一鸣", "计算机 2302"), ("2023010150", "郑雅心", "计算机 2302")]
rows = []
for i, (uid, un, rn, dept, _, _, _) in enumerate(users):
    av = f"/uploads/seed/avatar/{(i % 8) + 1:02d}.jpg"
    rows.append(f"({uid},'{un}','{PWD}','{rn}','1380000{1000 + uid}','{un}@univ.edu.cn','{av}',{dept},NULL,1)")
for i, (no, name, cls) in enumerate(students):
    uid = 11 + i
    av = f"/uploads/seed/avatar/{((i + 3) % 8) + 1:02d}.jpg"
    rows.append(f"({uid},'{no}','{PWD}','{name}','1390000{2000 + i}','{no}@stu.univ.edu.cn','{av}',3,'{cls}',1)")
w("INSERT INTO `sys_user`(`id`,`username`,`password`,`real_name`,`phone`,`email`,`avatar`,`dept_id`,`class_name`,`status`) VALUES\n" +
  ",\n".join(rows) + ";")

ur = [(1, 1), (2, 2), (3, 2), (4, 3), (5, 3), (6, 4), (7, 4)] + [(11 + i, 5) for i in range(8)]
w("INSERT INTO `sys_user_role`(`user_id`,`role_id`) VALUES " + ",".join(f"({a},{b})" for a, b in ur) + ";")

subjects = [(1, "XK001", "高等数学", "本科", 2, 2, 0, 60.00, 1),
            (2, "XK002", "数据结构", "本科", 3, 4, 0, 60.00, 2),
            (3, "XK003", "大学物理", "本科", 4, 5, 0, 60.00, 3),
            (4, "XK004", "线性代数", "本科", 2, 2, 0, 60.00, 4),
            (5, "XK005", "程序设计基础", "本科", 3, 4, 0, 60.00, 5)]
w("INSERT INTO `subject`(`id`,`subject_no`,`subject_name`,`edu_level`,`dept_id`,`owner_id`,`sort_no`,`pass_rate`,`status`,`create_time`) VALUES " +
  ",".join(f"({a},'{b}','{c}','{d}',{e},{f},{a},60.00,1,'2026-0{(a % 3) + 3}-1{a} 09:20:00')" for a, b, c, d, e, f, g, h, i in subjects) +
  ",(6,'XK006','离散数学','本科',3,3,6,60.00,0,'2026-04-12 10:00:00');")

# 知识点树
kp_defs = [
    # (subject_id, parent_name_or_None, name, weight, level)
    (1, None, "函数与极限", 22), (1, "函数与极限", "数列极限", 8), (1, "函数与极限", "函数连续性", 6),
    (1, "函数与极限", "无穷小比较", 4), (1, "函数与极限", "两个重要极限", 4),
    (1, None, "一元函数微分学", 26), (1, "一元函数微分学", "导数定义与计算", 10),
    (1, "一元函数微分学", "微分中值定理", 8), (1, "一元函数微分学", "导数应用", 8),
    (1, None, "一元函数积分学", 30), (1, "一元函数积分学", "不定积分", 10),
    (1, "不定积分", "换元积分法", 4), (1, "不定积分", "分部积分法", 3), (1, "不定积分", "有理函数积分", 3),
    (1, "一元函数积分学", "定积分", 12), (1, "一元函数积分学", "定积分应用", 8),
    (1, None, "多元函数微积分", 16), (1, "多元函数微积分", "偏导数与全微分", 9), (1, "多元函数微积分", "二重积分", 7),
    (1, None, "常微分方程", 6),
    (2, None, "线性表", 25), (2, "线性表", "顺序表与链表", 13), (2, "顺序表与链表", "指针与引用", 6),
    (2, "线性表", "栈与队列", 12),
    (2, None, "树与二叉树", 35), (2, "树与二叉树", "二叉树遍历", 15), (2, "树与二叉树", "二叉搜索树", 10),
    (2, "树与二叉树", "平衡树", 10),
    (2, None, "图", 20), (2, "图", "图的遍历", 10), (2, "图", "最短路径", 10),
    (2, None, "查找与排序", 20), (2, "查找与排序", "排序算法", 12), (2, "查找与排序", "哈希查找", 8),
    (3, None, "力学", 30), (3, "力学", "牛顿运动定律", 15), (3, "力学", "动量与能量", 15),
    (3, None, "电磁学", 40), (3, "电磁学", "静电场", 15), (3, "电磁学", "电磁感应", 15),
    (3, "电磁学", "恒定磁场", 10),
    (3, None, "光学", 30), (3, "光学", "光的干涉", 15), (3, "光学", "光的衍射", 15),
    (4, None, "行列式", 20), (4, None, "矩阵", 30), (4, "矩阵", "矩阵运算", 15), (4, "矩阵", "矩阵的秩", 15),
    (4, None, "向量组", 20), (4, None, "特征值与二次型", 30), (4, "特征值与二次型", "特征值与特征向量", 18),
    (4, "特征值与二次型", "二次型", 12),
    (5, None, "语法基础", 30), (5, "语法基础", "数据类型", 15), (5, "语法基础", "流程控制", 15),
    (5, None, "函数与模块", 30), (5, "函数与模块", "函数定义", 15), (5, "函数与模块", "递归", 15),
    (5, None, "文件与异常", 40), (5, "文件与异常", "文件读写", 20), (5, "文件与异常", "异常处理", 20),
]
kp_rows, kp_id, kp_map = [], 1, {}
for i, (sid, parent, name, weight) in enumerate(kp_defs):
    pid = kp_map.get((sid, parent), 0)
    lvl = 1 if parent is None else (2 if parent in [n for s, p, n, _ in kp_defs if p is None] else 3)
    code = f"ZS{sid:02d}{kp_id:04d}"
    kp_rows.append((kp_id, code, sid, pid, name, lvl, weight, 1))
    kp_map[(sid, name)] = kp_id
    kp_id += 1
w("INSERT INTO `knowledge_point`(`id`,`kp_no`,`subject_id`,`parent_id`,`kp_name`,`kp_level`,`exam_weight`,`status`) VALUES\n" +
  ",\n".join(f"({a},'{b}',{c},{d},'{e}',{f},{g:.2f},{h})" for a, b, c, d, e, f, g, h in kp_rows) + ";")

# 题目
QS = [
    # (sid, kp, type, stem, answer, analysis, diff, score, source, status, opts)
    (1, "换元积分法", "单选", "计算不定积分 ∫ 2x·cos(x²) dx，正确结果是（ ）", "A",
     "令 u = x²，则 du = 2x dx，原式化为 ∫ cos u du = sin u + C，回代得 sin(x²) + C。易错点是把系数误乘 2 或忘记回代。",
     0.55, 5.0, "教材", "已入库",
     [("sin(x²) + C", 1, "换元后直接积分再回代，结果正确"),
      ("2sin(x²) + C", 0, "误把 du 的系数当成积分结果系数"),
      ("cos(x²) + C", 0, "混淆 sin 与 cos 的原函数"),
      ("x²sin(x²) + C", 0, "把 u 直接当作系数保留")]),
    (1, "导数应用", "计算", "求函数 y = x³ - 3x 的单调区间与极值。", "递增区间 (-∞,-1) 与 (1,+∞)，递减区间 (-1,1)；极大值 f(-1)=2，极小值 f(1)=-2",
     "先求导 y' = 3x² - 3 = 3(x-1)(x+1)，令导数为零得驻点 x = ±1；按区间判断导数符号得到单调性，再由符号变化判定极大值与极小值。", 0.72, 12.0, "真题", "已入库", []),
    (1, "两个重要极限", "填空", "lim(x→0) sin 3x / x = ____", "3",
     "利用重要极限 lim(x→0) sin x / x = 1，把式子变形为 3·sin3x/(3x)，极限为 3×1 = 3。也可用等价无穷小 sin3x ~ 3x 直接得到。",
     0.35, 4.0, "教材", "已入库", []),
    (1, "定积分", "填空", "定积分 ∫₀¹ x² dx 的值为 ____", "1/3",
     "由牛顿-莱布尼茨公式，原函数为 x³/3，代入上下限得 1/3 - 0 = 1/3。注意定积分结果是数值而非函数。", 0.32, 4.0, "教材", "已入库", []),
    (1, "函数连续性", "单选", "函数 f(x) = |x| 在 x = 0 处（ ）", "B",
     "f(x)=|x| 在 x=0 处左右极限都等于 0 且等于函数值，故连续；但左导数为 -1、右导数为 1，导数不存在，因此不可导。",
     0.44, 5.0, "真题", "已入库",
     [("连续且可导", 0, "忽略了尖点处左右导数不等"),
      ("连续但不可导", 1, "左右极限相等但左右导数不等，正确"),
      ("不连续但可导", 0, "可导必连续，逻辑矛盾"),
      ("既不连续也不可导", 0, "极限存在且等于函数值，实际连续")]),
    (1, "分部积分法", "多选", "下列积分中可以使用分部积分法求解的有（ ）", "A,C",
     "分部积分适用于被积函数为“代数×超越”型或含反三角函数、对数函数的积分。∫x·e^x dx 与 ∫x·ln x dx 均符合，而 ∫sin²x dx 宜用降幂公式，∫1/(1+x²) dx 是基本积分公式直接得出。",
     0.62, 5.0, "自建", "已入库",
     [("∫ x·e^x dx", 1, "代数×指数，标准分部积分"),
      ("∫ sin²x dx", 0, "应使用降幂公式而非分部积分"),
      ("∫ x·ln x dx", 1, "代数×对数，需先取 u = ln x"),
      ("∫ 1/(1+x²) dx", 0, "基本积分公式，直接得 arctan x")]),
    (1, "微分中值定理", "判断", "若函数在闭区间上连续、开区间内可导，则一定存在一点使导数为零。", "错",
     "这是罗尔定理的结论，还需要补充条件 f(a) = f(b)。仅有连续与可导不能保证存在导数为零的点，例如 f(x)=x 在 [0,1] 上导数恒为 1。",
     0.30, 2.0, "自建", "已入库",
     [("对", 0, "遗漏了端点函数值相等这一条件"),
      ("错", 1, "缺少 f(a)=f(b) 条件，结论不成立")]),
    (1, "数列极限", "单选", "数列 {1/n} 的极限是（ ）", "A",
     "当 n 趋于无穷时 1/n 趋于 0，由极限定义，对任意 ε>0 取 N = [1/ε]+1 即可使 n>N 时 |1/n| < ε。",
     0.25, 3.0, "教材", "已入库",
     [("0", 1, "正确，1/n 单调递减趋于 0"), ("1", 0, "误认为首项即极限"),
      ("无穷大", 0, "与 n 本身混淆"), ("不存在", 0, "极限确实存在")]),
    (1, "偏导数与全微分", "计算", "设 z = x²y + sin(xy)，求全微分 dz。", "dz = (2xy + y·cos(xy))dx + (x² + x·cos(xy))dy",
     "先求偏导：∂z/∂x = 2xy + y·cos(xy)，∂z/∂y = x² + x·cos(xy)。由全微分公式 dz = z_x dx + z_y dy 即得结果。",
     0.78, 12.0, "真题", "已入库", []),
    (1, "二重积分", "简答", "简述在极坐标下计算二重积分时面积元素如何变换，并说明适用情形。", "面积元素 dxdy 变为 r dr dθ；当积分区域为圆或扇形、被积函数含 x²+y² 时适用",
     "极坐标变换 x = r cosθ，y = r sinθ，雅可比行列式为 r，因此 dxdy = r dr dθ。圆形区域或含平方和的被积函数用极坐标可显著简化计算。",
     0.66, 8.0, "自建", "已入库", []),
    (1, "有理函数积分", "单选", "∫ 1/(x²-1) dx 的结果是（ ）", "C",
     "先部分分式分解 1/(x²-1) = 1/2·[1/(x-1) - 1/(x+1)]，积分得 (1/2)ln|(x-1)/(x+1)| + C。",
     0.70, 5.0, "自建", "已入库",
     [("ln|x²-1| + C", 0, "直接套用 ln 形式，漏掉分解系数"),
      ("arctan x + C", 0, "与 1/(1+x²) 混淆"),
      ("(1/2)ln|(x-1)/(x+1)| + C", 1, "部分分式分解后积分，正确"),
      ("(1/2)ln|x²-1| + C", 0, "缺少分母差式，系数错误")]),
    (1, "无穷小比较", "判断", "当 x→0 时，x² 是比 x 高阶的无穷小。", "对",
     "两者之比 x²/x = x → 0，按定义 x² 是 x 的高阶无穷小，记作 x² = o(x)。理解阶的比较有助于等价无穷小替换。",
     0.28, 2.0, "教材", "已入库",
     [("对", 1, "比值趋于 0，确为高阶无穷小"), ("错", 0, "阶的判断依据是比值极限")]),
    (1, "导数定义与计算", "填空", "设 f(x) = x² + 2x，则 f'(1) = ____", "4",
     "f'(x) = 2x + 2，代入 x = 1 得 4。也可用导数定义取极限 (f(1+h)-f(1))/h 验证，结果一致。", 0.40, 4.0, "教材", "已入库", []),
    (1, "定积分应用", "计算", "求曲线 y = x² 与直线 y = 2x 所围成的图形面积。", "4/3",
     "先求交点：x² = 2x 得 x = 0 与 x = 2。面积 S = ∫₀² (2x - x²) dx = [x² - x³/3]₀² = 4 - 8/3 = 4/3。",
     0.68, 10.0, "真题", "已入库", []),
    (1, "常微分方程", "单选", "微分方程 y' = 2y 的通解是（ ）", "B",
     "分离变量 dy/y = 2dx，两边积分得 ln|y| = 2x + C₁，即 y = C·e^(2x)。这是一阶线性齐次方程的标准解法。",
     0.58, 5.0, "教材", "已入库",
     [("y = C·e^(-2x)", 0, "指数符号写反"),
      ("y = C·e^(2x)", 1, "分离变量积分后取指数，正确"),
      ("y = 2x + C", 0, "把微分方程当作代数方程"),
      ("y = C·x²", 0, "误按幂函数求解")]),
    (2, "二叉树遍历", "单选", "对二叉树进行中序遍历，得到的序列（ ）", "C",
     "中序遍历顺序为「左子树 → 根 → 右子树」。对二叉搜索树而言中序序列恰好是递增有序序列，这一性质常用于验证与查找。",
     0.55, 5.0, "真题", "已入库",
     [("先访问根结点", 0, "那是先序遍历"),
      ("按层从上到下访问", 0, "那是层序遍历"),
      ("左子树、根、右子树依次访问", 1, "中序定义，正确"),
      ("右子树、根、左子树依次访问", 0, "顺序颠倒")]),
    (2, "指针与引用", "简答", "简述 C 语言中指针与引用的区别，并各举一例。", "指针是保存地址的变量可重新赋值、可为空；引用是别名必须初始化且绑定后不可更改",
     "指针本身是变量，占用独立存储空间，可以指向不同对象，也可以为 NULL，使用前需判空；引用是已存在对象的别名，必须在定义时初始化，之后不能再绑定其他对象。例如 int *p = &a 与 int &r = a。",
     0.68, 10.0, "自建", "已入库", []),
    (2, "排序算法", "单选", "下列排序算法中，平均时间复杂度为 O(nlogn) 且不稳定的是（ ）", "A",
     "快速排序平均 O(nlogn)，但相同元素的相对次序可能改变，属于不稳定排序。归并排序稳定但需要额外空间；冒泡与插入为 O(n²)。",
     0.60, 5.0, "真题", "已入库",
     [("快速排序", 1, "平均 O(nlogn)，不稳定，正确"),
      ("归并排序", 0, "平均 O(nlogn)，但稳定"),
      ("冒泡排序", 0, "平均 O(n²)"),
      ("插入排序", 0, "平均 O(n²)，且稳定")]),
    (2, "最短路径", "简答", "说明 Dijkstra 算法为什么不能处理含负权边的图。", "因为算法基于贪心，认为已确定的最短距离不会再被更新，负权边会破坏这一前提",
     "Dijkstra 每次选取当前距离最小的未访问结点并确定其最短路径，这依赖于「边权非负」才能保证后续路径不会更短。若存在负权边，已确定的结点距离仍可能被后续路径减小，导致结果错误，此时应使用 Bellman-Ford 算法。",
     0.75, 10.0, "教材", "已入库", []),
    (2, "哈希查找", "填空", "在装填因子为 0.75 的开放地址哈希表中，平均查找长度的主要影响因素是 ____。", "装填因子",
     "开放地址法的平均查找长度只与装填因子 α 有关，α 越大冲突越多，查找长度增长越快。因此通常控制 α ≤ 0.75 并在超限时扩容。",
     0.62, 4.0, "自建", "待审核", []),
    (2, "平衡树", "判断", "AVL 树中任意结点的左右子树高度差的绝对值不超过 1。", "对",
     "这是 AVL 树的平衡条件。插入或删除后若某结点平衡因子绝对值超过 1，需通过 LL、RR、LR、RL 四种旋转恢复平衡，从而保证树高为 O(logn)。",
     0.35, 2.0, "教材", "已入库",
     [("对", 1, "AVL 平衡因子定义如此"), ("错", 0, "混淆了红黑树与 AVL 树的条件")]),
    (2, "栈与队列", "单选", "若入栈序列为 1,2,3,4，则下列不可能的出栈序列是（ ）", "D",
     "栈的后进先出特性决定了出栈序列必须满足「不存在 i<j<k 使得出栈顺序为 k,i,j」的约束。4,3,1,2 中 1 在 2 之前出栈而 2 比 1 后入栈，且 3 已先出，违反栈规则。",
     0.72, 5.0, "真题", "已入库",
     [("1,2,3,4", 0, "边入边出即可实现"),
      ("4,3,2,1", 0, "全部入栈后再出栈"),
      ("2,1,4,3", 0, "先入 1,2 出 2,1，再入 3,4 出 4,3"),
      ("4,3,1,2", 1, "3 先于 1 出栈时 2 必在 1 之前，此序列不可能")]),
    (2, "图的遍历", "填空", "对含 n 个顶点、e 条边的图做广度优先遍历，时间复杂度为 ____。", "O(n+e)",
     "邻接表存储时每个顶点入队一次、每条边被检查两次，故为 O(n+e)；邻接矩阵存储时为 O(n²)。BFS 常用于求无权图最短路径。",
     0.64, 4.0, "教材", "已入库", []),
    (3, "电磁感应", "单选", "关于楞次定律，下列说法正确的是（ ）", "B",
     "楞次定律指出感应电流的磁场总是阻碍引起感应电流的磁通量变化。它是能量守恒在电磁感应中的体现，因此感应电流方向总是反抗而非顺从原变化。",
     0.50, 5.0, "真题", "已入库",
     [("感应电流方向与原磁场方向相同", 0, "混淆了阻碍变化与同向"),
      ("感应电流的磁场阻碍原磁通量的变化", 1, "楞次定律原文表述，正确"),
      ("感应电动势大小与磁通量成正比", 0, "那是法拉第定律，且应为变化率"),
      ("感应电流方向由安培定则直接判定", 0, "安培定则用于电流推磁场方向")]),
    (3, "静电场", "计算", "真空中两点电荷 q1 = 2×10⁻⁶ C、q2 = -2×10⁻⁶ C 相距 0.1 m，求连线中点处的电场强度。", "7.2×10⁶ N/C，方向由 q1 指向 q2",
     "中点处两电荷产生的场强同向叠加：E = k·q/(r/2)² × 2 = 9×10⁹ × 2×10⁻⁶ / 0.05² × 2 = 7.2×10⁶ N/C，方向由正电荷指向负电荷。",
     0.80, 12.0, "真题", "已入库", []),
    (3, "光的干涉", "判断", "杨氏双缝干涉实验中，相邻明条纹间距与双缝间距成正比。", "错",
     "条纹间距 Δx = Lλ/d，与双缝间距 d 成反比，与屏距 L 和波长 λ 成正比。缝距越小条纹越稀疏，这是判断该题的关键。",
     0.42, 2.0, "教材", "已入库",
     [("对", 0, "把反比关系误记为成正比"), ("错", 1, "Δx = Lλ/d，与 d 成反比")]),
    (3, "牛顿运动定律", "单选", "物体做匀速圆周运动时，其所受合外力（ ）", "B",
     "匀速圆周运动速度大小不变但方向不断改变，加速度为向心加速度，方向指向圆心，因此合外力提供向心力且与速度方向垂直，不做功。",
     0.38, 5.0, "教材", "已入库",
     [("为零", 0, "误认为匀速即合力为零"),
      ("指向圆心，大小为 mv²/r", 1, "提供向心加速度，正确"),
      ("沿速度方向", 0, "沿速度方向会改变速率"),
      ("背离圆心", 0, "方向相反，属于离心效果误解")]),
    (4, "特征值与特征向量", "单选", "设 3 阶矩阵 A 的三个特征值为 1、2、3，则 |A| = （ ）", "C",
     "矩阵行列式等于全部特征值之积，即 1×2×3 = 6。同时矩阵的迹等于特征值之和 6，可作为验算。",
     0.52, 5.0, "真题", "已入库",
     [("3", 0, "误取最大特征值"), ("5", 0, "误取特征值之和中的部分"),
      ("6", 1, "行列式等于特征值之积，正确"), ("0", 0, "只有存在零特征值时为 0")]),
    (4, "矩阵的秩", "填空", "若 4×5 矩阵 A 的秩为 3，则其齐次线性方程组 Ax=0 的基础解系含 ____ 个向量。", "2",
     "基础解系向量个数为 n - r = 5 - 3 = 2，其中 n 为未知量个数（列数），r 为矩阵的秩。这是解空间维数公式的直接应用。",
     0.66, 4.0, "教材", "已入库", []),
    (4, "二次型", "简答", "判断二次型 f = x₁² + 2x₂² + 3x₃² 的正定性，并说明依据。", "正定，因为标准形系数全为正（顺序主子式均大于零）",
     "该二次型已是标准形，三个平方项系数 1、2、3 均大于零；等价地，其矩阵为对角阵 diag(1,2,3)，各阶顺序主子式 1、2、6 均大于零，故正定。",
     0.70, 8.0, "自建", "已入库", []),
    (5, "流程控制", "单选", "在 C 语言中，for 循环 for(i=0;i<10;i++) 的循环体共执行（ ）次", "C",
     "i 从 0 开始，每次递增 1，当 i 等于 10 时条件不成立退出，因此共执行 10 次（i = 0 到 9）。注意循环次数为终值减初值。",
     0.30, 3.0, "教材", "已入库",
     [("9", 0, "把 i<10 误当成 i<=9 的排他计数"), ("10", 1, "i 取值 0-9 共 10 次，正确"),
      ("11", 0, "多算了退出判断的那一次"), ("0", 0, "条件初次即成立")]),
    (5, "异常处理", "简答", "说明 try-catch-finally 中 finally 块的执行时机及其典型用途。", "无论是否发生异常都会执行，常用于释放资源",
     "finally 块在 try 或 catch 执行结束后必然执行，即使 try 中有 return 也会先执行 finally。典型用途是关闭文件、释放锁、断开数据库连接等资源清理工作，保证不因异常泄漏资源。",
     0.64, 8.0, "自建", "已入库", []),
    (5, "递归", "计算", "写出求 n! 的递归函数的核心代码，并说明递归终止条件。", "int f(int n){ if(n<=1) return 1; return n*f(n-1); } 终止条件 n<=1",
     "递归必须包含终止条件与递推关系。n! 的终止条件是 n ≤ 1 时返回 1，递推关系为 f(n) = n × f(n-1)。缺少终止条件会导致栈溢出。",
     0.60, 10.0, "教材", "已入库", []),
    (1, "换元积分法", "单选", "∫ x·e^(x²) dx 的结果是（ ）", "A",
     "令 u = x²，du = 2x dx，则 x dx = du/2，原式 = 1/2∫e^u du = 1/2·e^(x²) + C。关键是识别出 x dx 正好是 du 的一半。",
     0.58, 5.0, "自建", "已入库",
     [("(1/2)e^(x²) + C", 1, "换元后系数为 1/2，正确"),
      ("e^(x²) + C", 0, "漏掉 1/2 系数"),
      ("x²e^(x²) + C", 0, "把 u 当作系数保留"),
      ("2e^(x²) + C", 0, "系数方向搞反")]),
    (1, "导数应用", "简答", "说明如何用导数判断函数在区间上的单调性。", "求导后看导数符号：大于零递增，小于零递减",
     "在区间内若 f'(x) > 0 则函数单调递增，f'(x) < 0 则单调递减。据此可先求驻点划分区间，再逐区间判断导数符号，同时可确定极值点。",
     0.45, 8.0, "自建", "待审核", []),
    (2, "图的遍历", "计算", "给定邻接矩阵，写出从顶点 1 出发的深度优先遍历序列。", "1,2,4,3,5",
     "DFS 沿一条路径尽可能深入再回溯。从 1 出发按编号升序访问邻接点，依次得到 1→2→4，回溯到 2 后访问 3，再回到 1 访问 5，序列为 1,2,4,3,5。",
     0.62, 10.0, "自建", "待审核", []),
    (3, "恒定磁场", "填空", "长直载流导线在距离 r 处产生的磁感应强度大小为 ____。", "μ₀I/(2πr)",
     "由安培环路定理，取以导线为轴的圆形环路，B·2πr = μ₀I，故 B = μ₀I/(2πr)。磁场方向由右手螺旋定则确定。",
     0.55, 4.0, "教材", "待审核", []),
    (4, "矩阵运算", "判断", "两个同阶矩阵相乘满足交换律。", "错",
     "矩阵乘法一般不满足交换律，AB ≠ BA。只有当两个矩阵可交换（如其中一个为数量矩阵）时才成立。这是矩阵运算与实数运算的重要差异。",
     0.30, 2.0, "教材", "待审核",
     [("对", 0, "把实数乘法性质直接套用"), ("错", 1, "矩阵乘法一般不满足交换律")]),
    (5, "文件读写", "单选", "以 \"r\" 模式打开一个不存在的文件，结果是（ ）", "B",
     "fopen 以只读模式打开不存在的文件会失败并返回 NULL，不会创建新文件。若需创建应使用 \"w\" 或 \"a\" 模式，调用后必须检查返回值再操作。",
     0.40, 3.0, "教材", "草稿",
     [("创建空文件并返回句柄", 0, "r 模式不创建文件"),
      ("返回 NULL，打开失败", 1, "只读模式要求文件已存在，正确"),
      ("创建空文件并报警告", 0, "混淆了 w 模式的行为"),
      ("程序直接崩溃", 0, "只是返回空指针，需自行判空")]),
    (1, "微分中值定理", "简答", "叙述拉格朗日中值定理的条件与结论。", "闭区间连续、开区间可导，则存在一点使 f(b)-f(a)=f'(ξ)(b-a)",
     "若函数 f(x) 在 [a,b] 上连续、在 (a,b) 内可导，则至少存在一点 ξ ∈ (a,b)，使得 f(b) - f(a) = f'(ξ)(b - a)。它是罗尔定理的推广，也是证明不等式与函数单调性的重要工具。",
     0.52, 8.0, "教材", "已退回", []),
    (2, "二叉搜索树", "单选", "在二叉搜索树中查找关键字 42，若当前结点为 50，则应（ ）", "A",
     "二叉搜索树满足左子树所有结点小于根、右子树所有结点大于根。42 < 50 因此应进入左子树继续查找，逐层比较直到命中或到达空指针。",
     0.34, 5.0, "教材", "已退回",
     [("进入左子树继续查找", 1, "42 小于 50，走左子树，正确"),
      ("进入右子树继续查找", 0, "方向判断相反"),
      ("直接返回未找到", 0, "尚未比较完全部路径"),
      ("从根重新开始查找", 0, "造成死循环")]),
    (1, "数列极限", "填空", "数列极限 lim(n→∞) (1 + 1/n)^n = ____", "e",
     "这是重要极限的数列形式，其极限为自然常数 e ≈ 2.71828。可由二项式展开证明数列单调递增且有上界，从而收敛于 e。",
     0.48, 4.0, "教材", "已停用", []),
    (2, "排序算法", "判断", "归并排序在最坏情况下的时间复杂度仍为 O(nlogn)。", "对",
     "归并排序每次都把序列二分后合并，递归深度为 logn，每层合并代价 O(n)，故最好、平均与最坏情况均为 O(nlogn)，代价是需要 O(n) 辅助空间。",
     0.36, 2.0, "教材", "已停用",
     [("对", 1, "归并排序各情况均为 O(nlogn)"), ("错", 0, "与快速排序的最坏情况混淆")]),
    (1, "函数与极限", "简答", "说明函数在一点连续需要满足的三个条件。", "该点有定义、极限存在、极限值等于函数值",
     "函数 f(x) 在 x₀ 处连续需同时满足：f(x₀) 有定义；lim(x→x₀) f(x) 存在；该极限等于 f(x₀)。三者缺一不可，任何一条不满足即为间断点。",
     0.42, 8.0, "教材", "已入库", []),
    (5, "数据类型", "单选", "在 C 语言中，sizeof(char) 的值是（ ）", "A",
     "C 标准规定 sizeof(char) 恒为 1，即 char 占 1 个字节。其他类型的大小由实现决定，但通常 int 为 4 字节、double 为 8 字节。",
     0.22, 3.0, "教材", "已入库",
     [("1", 1, "标准规定 char 占 1 字节，正确"), ("2", 0, "与 short 混淆"),
      ("4", 0, "与 int 混淆"), ("由编译器决定", 0, "char 的大小是标准固定的")]),
]

q_rows, opt_rows, q_meta = [], [], []
qid = 1
subj_code = {1: "01", 2: "02", 3: "03", 4: "04", 5: "05"}
day_off = 175
for (sid, kp, typ, stem, ans, ana, diff, score, src, status, opts) in QS:
    qno = f"TM{subj_code[sid]}{qid:06d}"
    kpid = kp_map.get((sid, kp))
    if kpid is None:
        # 兜底：按名称在同学科内查找
        kpid = next((v for (s, n), v in kp_map.items() if s == sid and n == kp), 0)
    ctime = (BASE - dt.timedelta(days=day_off % 170, hours=(qid * 7) % 20, minutes=(qid * 13) % 60)).strftime("%Y-%m-%d %H:%M:%S")
    day_off -= 4
    q_rows.append(f"({qid},'{qno}',{sid},{kpid},'{typ}','{esc(stem)}','{esc(ans)}','{esc(ana)}',{diff},{score},'{src}',0,'{status}',4,'{ctime}')")
    q_meta.append((qid, sid, kpid, typ, stem, ans, score, diff, status, ctime))
    for j, (content, correct, note) in enumerate(opts):
        label = chr(65 + j)
        opt_rows.append(f"({qid},'{label}','{esc(content)}',{correct},{j + 1},NULL,'{esc(note)}')")
    qid += 1

w("INSERT INTO `question`(`id`,`question_no`,`subject_id`,`knowledge_point_id`,`question_type`,`stem`,`answer`,`analysis`,`difficulty`,`score`,`source_type`,`correct_rate`,`status`,`create_by`,`create_time`) VALUES\n" +
  ",\n".join(q_rows) + ";")
w("INSERT INTO `question_option`(`question_id`,`option_label`,`option_content`,`is_correct`,`sort_no`,`image_url`,`distractor_note`) VALUES\n" +
  ",\n".join(opt_rows) + ";")

# 图片驱动：给 8 道"图形/公式"相关题目的首个选项挂本地图片
fig_targets = [q for q in q_meta if q[3] in ("计算", "单选")][:8]
for idx, q in enumerate(fig_targets, 1):
    w(f"UPDATE `question_option` SET `image_url`='/uploads/seed/figure/{idx:02d}.jpg' "
      f"WHERE `question_id`={q[0]} AND `option_label`='A';")

# 试卷
papers = [(1, "SJ2604010001", "高等数学 期中测评卷 A", 1, "随机", 90, "使用中", 90, "按知识点权重抽题，难度 0.30-0.80，共 20 题"),
          (2, "SJ2604010002", "数据结构 单元测验（树与图）", 2, "手动", 45, "已发布", 45, None),
          (3, "SJ2603280007", "线性代数 期末模拟卷", 4, "随机", 100, "已归档", 100, "按章节权重抽题，难度 0.40-0.90，共 22 题"),
          (4, "SJ2603250003", "高等数学 错题重练卷（第 3 周）", 1, "错题重练", 30, "已发布", 30, None),
          (5, "SJ2603200001", "大学物理 电磁学专项", 3, "手动", 80, "待审核", 80, None),
          (6, "SJ2603180005", "程序设计基础 第 2 章练习", 5, "手动", 40, "草稿", 40, None),
          (7, "SJ2603100002", "高等数学 补考卷", 1, "随机", 90, "已驳回", 90, "按知识点权重抽题，难度 0.20-0.70，共 20 题"),
          (8, "SJ2602280004", "数据结构 期末测评卷", 2, "随机", 100, "已归档", 100, "按章节权重抽题，难度 0.30-0.90，共 22 题")]
pq_rows, pq_id = [], 1
paper_meta = []
for (pid, pno, pname, sid, mode, dur, status, tscore, rule) in papers:
    cands = [q for q in q_meta if q[1] == sid and q[8] == "已入库"]
    n = min(len(cands), 8 if pid in (4, 6) else 10)
    picked = cands[:n]
    if not picked:
        continue
    per = round(tscore / n, 1)
    sec = 1
    for k, q in enumerate(picked, 1):
        pq_rows.append(f"({pid},{q[0]},{sec},{k},{per},'{q[3]}',{q[2]},'{esc(q[4])}',4)")
        pq_id += 1
    rej = "题目分值合计与总分不一致，请调整后重新提交" if status == "已驳回" else "NULL"
    rej_sql = f"'{rej}'" if status == "已驳回" else "NULL"
    ctime = (BASE - dt.timedelta(days=(pid * 11) % 150 + 10)).strftime("%Y-%m-%d %H:%M:%S")
    paper_meta.append((pid, sid, pname, status, n, tscore, picked, ctime))
    w(f"INSERT INTO `paper`(`id`,`paper_no`,`paper_name`,`subject_id`,`build_mode`,`question_count`,`total_score`,`duration_min`,`difficulty_avg`,`random_rule`,`creator_id`,`status`,`reject_reason`,`create_by`,`create_time`) "
      f"VALUES ({pid},'{pno}','{pname}',{sid},'{mode}',{n},{tscore},{dur},"
      f"{round(sum(q[7] for q in picked) / len(picked), 2)},{'NULL' if not rule else repr(rule).replace(chr(39), chr(39))},4,'{status}',{rej_sql},4,'{ctime}');")
w("INSERT INTO `paper_question`(`paper_id`,`question_id`,`section_no`,`sort_no`,`score`,`question_type`,`knowledge_point_id`,`stem_snapshot`,`create_by`) VALUES\n" +
  ",\n".join(pq_rows) + ";")

# 练习记录 + 作答明细 + 错题本
students_id = [11, 12, 13, 14, 15, 16, 17, 18]
rec_rows, ans_rows, wrong_rows, plan_rows = [], [], [], []
rid, aid = 1, 1
wrong_keys = {}
plans = []
statuses_cycle = ["已交卷", "已批阅", "已交卷", "已作废", "已交卷", "进行中"]
for i in range(48):
    stu = students_id[i % 8]
    pm = paper_meta[i % len(paper_meta)]
    pid, sid, pname, pstatus, n, tscore, picked, pctime = pm
    st = statuses_cycle[i % len(statuses_cycle)]
    # 练习时间覆盖近 4 个月，且近 30 天保持足够样本（掌握度诊断按近 30 天统计）
    day_buckets = [0, 2, 4, 7, 11, 16, 22, 28, 36, 48, 62, 80, 100]
    days = day_buckets[i % len(day_buckets)] + (i // len(day_buckets)) * 3
    start = BASE - dt.timedelta(days=days, hours=(i * 5) % 12 + 1, minutes=(i * 17) % 60)
    typ = ["试卷练习", "试卷练习", "知识点练习", "错题重练"][i % 4]
    qcount = len(picked)
    if st == "进行中":
        submit, used, cc, gs, qcount_done = "NULL", 0, 0, 0.0, max(3, qcount // 2)
        rec_rows.append(f"({rid},'LX{start.strftime('%y%m%d')}{rid:06d}',{pid if typ != '错题重练' else 'NULL'},{stu},'{typ}',"
                        f"'{start.strftime('%Y-%m-%d %H:%M:%S')}',NULL,0,{qcount_done},0,0.0,'进行中',4,'{start.strftime('%Y-%m-%d %H:%M:%S')}')")
        rid += 1
        continue
    wrong_n = (i * 3) % max(2, qcount // 2)
    cc = max(0, qcount - wrong_n)
    per = tscore / qcount
    gs = round(cc * per, 1)
    used = min(86400, int((qcount * 95) + (i % 7) * 180))
    if i % 11 == 0:
        used = 7200  # 超时自动交卷
    submit = start + dt.timedelta(seconds=used)
    rec_rows.append(f"({rid},'LX{start.strftime('%y%m%d')}{rid:06d}',{pid if typ != '错题重练' else 'NULL'},{stu},'{typ}',"
                    f"'{start.strftime('%Y-%m-%d %H:%M:%S')}','{submit.strftime('%Y-%m-%d %H:%M:%S')}',{used},{qcount},{cc},{gs},'{st}',4,'{start.strftime('%Y-%m-%d %H:%M:%S')}')")
    wrong_flag = set(range(0, qcount, max(1, qcount // max(1, wrong_n)))) if wrong_n else set()
    for k, q in enumerate(picked):
        correct = 0 if k in wrong_flag else 1
        ua = "B" if correct == 0 else q[5][:40]
        ans_rows.append(f"({aid},{rid},{q[0]},{stu},{q[2]},'{ua}',{correct},{per if correct else 0},{per},{int(used / qcount) + (k % 5) * 20},'{submit.strftime('%Y-%m-%d %H:%M:%S')}')")
        aid += 1
        if correct == 0:
            key = (stu, q[0])
            if key in wrong_keys:
                wrong_keys[key][2] += 1
                wrong_keys[key][4] = submit
            else:
                wrong_keys[key] = [stu, q[0], 1, q[2], submit, rid, ua]
    rid += 1

wid = 1
for (stu, qid_, cnt, kpid, last_t, src_rec, ua) in list(wrong_keys.values())[:40]:
    sid_ = next(q[1] for q in q_meta if q[0] == qid_)
    state = ["未掌握", "复习中", "已掌握", "未掌握", "已移除"][wid % 5]
    streak = 2 if state == "已掌握" else (1 if state == "复习中" else 0)
    wc = cnt
    wtime = last_t.strftime("%Y-%m-%d %H:%M:%S")
    ctime = (last_t - dt.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    note = "换元时忘记回代" if wid % 3 == 0 else ("概念混淆，需重看教材" if wid % 3 == 1 else None)
    note_sql = f"'{esc(note)}'" if note else "NULL"
    wc_sql = f"'{ua}'" if wid % 4 else "NULL"
    wrong_rows.append(f"({wid},{stu},{qid_},{sid_},{kpid},{wc},'{wtime}',{wc_sql},{streak},{src_rec},'{state}',{note_sql},{stu},'{ctime}')")
    for d in (1, 3, 7):
        pd = (last_t + dt.timedelta(days=d)).date()
        if state == "已掌握":
            done, dtm, res = 1, (pd - dt.timedelta(days=1)).strftime("%Y-%m-%d 20:10:00"), "答对"
        elif pd < BASE.date() and wid % 2 == 0:
            done, dtm, res = 1, f"{pd} 21:05:00", ("答错" if wid % 6 == 0 else "答对")
        else:
            done, dtm, res = 0, "NULL", "NULL"
        dtm_sql = f"'{dtm}'" if done else "NULL"
        res_sql = f"'{res}'" if res != "NULL" else "NULL"
        plan_rows.append(f"({wid},{stu},{d},'{pd}',{done},{dtm_sql},{res_sql})")
    wid += 1

w("INSERT INTO `practice_record`(`id`,`record_no`,`paper_id`,`student_id`,`practice_type`,`start_time`,`submit_time`,`used_seconds`,`question_count`,`correct_count`,`got_score`,`status`,`create_by`,`create_time`) VALUES\n" +
  ",\n".join(rec_rows) + ";")
w("INSERT INTO `practice_answer`(`id`,`record_id`,`question_id`,`student_id`,`knowledge_point_id`,`user_answer`,`is_correct`,`got_score`,`full_score`,`used_seconds`,`create_time`) VALUES\n" +
  ",\n".join(ans_rows) + ";")
w("INSERT INTO `wrong_book`(`id`,`student_id`,`question_id`,`subject_id`,`knowledge_point_id`,`wrong_count`,`last_wrong_time`,`last_answer`,`correct_streak`,`source_record_id`,`status`,`note`,`create_by`,`create_time`) VALUES\n" +
  ",\n".join(wrong_rows) + ";")
w("INSERT INTO `wrong_review_plan`(`wrong_id`,`student_id`,`plan_day`,`plan_date`,`done_flag`,`done_time`,`result`) VALUES\n" +
  ",\n".join(plan_rows) + ";")

# 掌握度规则
w("""INSERT INTO `mastery_rule`(`id`,`rule_name`,`rule_version`,`w_accuracy`,`w_time`,`w_redo`,`w_weight`,`w_review`,`pass_level`,`good_level`,`weak_level`,`effect_time`,`status`,`remark`,`create_by`) VALUES
(1,'知识点掌握度诊断规则','v1',50.00,10.00,15.00,15.00,10.00,85.00,70.00,50.00,'2026-03-01 00:00:00','已归档','初版规则，正确率权重偏高',2),
(2,'知识点掌握度诊断规则','v2',45.00,15.00,20.00,10.00,10.00,85.00,70.00,50.00,'2026-08-15 00:00:00','已归档','提高耗时与重做表现权重，降低考纲权重影响',2),
(3,'知识点掌握度诊断规则','v3',40.00,15.00,20.00,15.00,10.00,85.00,70.00,50.00,'2026-10-01 00:00:00','生效中','恢复考纲权重至15%，与教学大纲对齐',2);""")

# 掌握度计算结果（32 条，含未测与边界）
mr_rows = []
rid2 = 1
lv = ["已掌握", "基本掌握", "薄弱", "严重薄弱", "未测"]
kp_list = [(kp_map[(s, n)], s) for (s, p, n, w) in kp_defs if (s, n) in kp_map]
seq = 0
for stu in students_id:
    for (kpid, sid) in kp_list[:8]:
        seq += 1
        if seq > 34:
            break
        sample = [3, 4, 5, 6, 8, 12, 18, 26][seq % 8]
        untested = seq % 11 == 0
        if untested:
            acc = tm = redo = wt = rv = 0.0
            total, level = 0.0, "未测"
        else:
            acc = round(20 + (seq * 13) % 78, 2)
            tm = round(10 + (seq * 17) % 88, 2)
            redo = round(30 + (seq * 11) % 65, 2)
            wt = round(20 + (seq * 7) % 80, 2)
            rv = round((seq * 19) % 100, 2)
            total = round(acc * 0.4 + tm * 0.15 + redo * 0.2 + wt * 0.15 + rv * 0.1, 2)
            level = "已掌握" if total >= 85 else ("基本掌握" if total >= 70 else ("薄弱" if total >= 50 else "严重薄弱"))
        man = "NULL"
        man_reason = "NULL"
        man_by = "NULL"
        man_time = "NULL"
        if seq % 9 == 0:
            man = "'薄弱'"
            man_reason = "'该班教学进度滞后，样本偏少导致正确率偏低，非掌握问题'"
            man_by = "2"
            man_time = "'2026-10-30 09:14:00'"
        snap = ('{"accuracy":%s,"timeRatio":%s,"redoRate":%s,"examWeight":%s,"reviewRate":%s,"sample":%d}' %
                (acc, round(tm / 100, 2), round(redo / 100, 2), round(wt / 100, 2), round(rv / 100, 2), sample))
        ct = (BASE - dt.timedelta(days=(seq * 3) % 90)).strftime("%Y-%m-%d 02:00:00")
        mr_rows.append(f"({rid2},{stu},{sid},{kpid},3,'v3',{acc},{tm},{redo},{wt},{rv},{total},'{level}',{sample},'{snap}',{man},{man_reason},{man_by},{man_time},'{ct}',{stu})")
        rid2 += 1
w("INSERT INTO `mastery_result`(`id`,`student_id`,`subject_id`,`knowledge_point_id`,`rule_id`,`rule_version`,`accuracy_score`,`time_score`,`redo_score`,`weight_score`,`review_score`,`total_score`,`level`,`sample_count`,`input_snapshot`,`manual_level`,`manual_reason`,`manual_by`,`manual_time`,`calc_time`,`create_by`) VALUES\n" +
  ",\n".join(mr_rows) + ";")

# 审核流水
au_rows = []
for i, q in enumerate([q for q in q_meta if q[8] in ("已入库", "已退回", "待审核")][:26], 1):
    qid_, sid, kpid, typ, stem, ans, score, diff, status, ctime = q
    if status == "待审核":
        continue
    res = "通过" if status == "已入库" else "退回"
    reason_t = "NULL" if res == "通过" else "'答案错误'"
    reason = "NULL" if res == "通过" else "'标准答案与解析不一致，请重新核对后提交'"
    at = (dt.datetime.strptime(ctime, "%Y-%m-%d %H:%M:%S") + dt.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    au_rows.append(f"({qid_},2,'{res}',{reason_t},{reason},1,'{at}')")
w("INSERT INTO `question_audit`(`question_id`,`auditor_id`,`audit_result`,`reason_type`,`reason`,`submit_times`,`audit_time`) VALUES\n" +
  ",\n".join(au_rows) + ";")

# 导入任务
w("""INSERT INTO `import_task`(`file_name`,`subject_id`,`total_rows`,`success_rows`,`fail_rows`,`fail_detail`,`status`,`operator_id`,`finish_time`,`create_by`,`create_time`) VALUES
('高数_第5章_积分.xlsx',1,120,118,2,'第 17 行：单选题正确项数为 2；第 43 行：知识点编码 ZS01-9999 不存在','已完成',2,'2026-10-30 09:12:00',2,'2026-10-30 09:08:00'),
('数据结构_树与图.xlsx',2,64,64,0,NULL,'已完成',3,'2026-10-29 15:40:00',3,'2026-10-29 15:36:00'),
('线代_矩阵.xlsx',4,50,39,11,'第 3/8/12/19 行：多选正确项不足 2 个；第 25/31 行：解析少于 20 字','部分失败',2,'2026-10-28 11:03:00',2,'2026-10-28 10:58:00'),
('物理_电磁学.xlsx',3,46,0,0,NULL,'执行中',5,NULL,5,'2026-11-01 06:50:00');""")

# 字典
dt_rows = [("题目状态", "question_status"), ("题型", "question_type"), ("来源类型", "source_type"),
           ("试卷状态", "paper_status"), ("组卷方式", "build_mode"), ("掌握状态", "wrong_status"),
           ("练习类型", "practice_type"), ("练习状态", "practice_status"), ("掌握等级", "mastery_level"),
           ("审核结果", "audit_result"), ("导入状态", "import_status"), ("适用层次", "edu_level")]
w("INSERT INTO `sys_dict_type`(`dict_name`,`dict_type`) VALUES " +
  ",".join(f"('{a}','{b}')" for a, b in dt_rows) + ";")

dd = {
    "question_status": [("草稿", "草稿"), ("待审核", "待审核"), ("已入库", "已入库"), ("已停用", "已停用"), ("已退回", "已退回")],
    "question_type": [("单选", "单选"), ("多选", "多选"), ("判断", "判断"), ("填空", "填空"), ("简答", "简答"), ("计算", "计算")],
    "source_type": [("自建", "自建"), ("真题", "真题"), ("教材", "教材"), ("引进", "引进")],
    "paper_status": [("草稿", "草稿"), ("待审核", "待审核"), ("已发布", "已发布"), ("使用中", "使用中"), ("已归档", "已归档"), ("已驳回", "已驳回")],
    "build_mode": [("手动", "手动"), ("随机", "随机"), ("错题重练", "错题重练")],
    "wrong_status": [("未掌握", "未掌握"), ("复习中", "复习中"), ("已掌握", "已掌握"), ("已移除", "已移除")],
    "practice_type": [("试卷练习", "试卷练习"), ("知识点练习", "知识点练习"), ("错题重练", "错题重练")],
    "practice_status": [("进行中", "进行中"), ("已交卷", "已交卷"), ("已批阅", "已批阅"), ("已作废", "已作废")],
    "mastery_level": [("已掌握", "已掌握"), ("基本掌握", "基本掌握"), ("薄弱", "薄弱"), ("严重薄弱", "严重薄弱"), ("未测", "未测")],
    "audit_result": [("通过", "通过"), ("退回", "退回")],
    "import_status": [("待执行", "待执行"), ("执行中", "执行中"), ("已完成", "已完成"), ("部分失败", "部分失败"), ("已失败", "已失败")],
    "edu_level": [("中职", "中职"), ("高职", "高职"), ("本科", "本科"), ("研究生", "研究生")]
}
dd_rows = []
for t, items in dd.items():
    for i, (lbl, val) in enumerate(items, 1):
        dd_rows.append(f"('{t}','{lbl}','{val}',{i},1)")
w("INSERT INTO `sys_dict_data`(`dict_type`,`dict_label`,`dict_value`,`sort_no`,`status`) VALUES\n" + ",\n".join(dd_rows) + ";")

# 菜单
MENUS = [
    (1, 0, "题库中心", "/question", None, None, "D", "book", 1),
    (2, 1, "题库统计首页", "/dashboard", "Dashboard", "stats:view", "M", "dashboard", 1),
    (3, 1, "学科管理", "/subject", "Subject", "subject:list", "M", "subject", 2),
    (4, 1, "知识点树", "/knowledge", "KnowledgeTree", "kp:list", "M", "tree", 3),
    (5, 1, "题库列表", "/question", "QuestionList", "question:list", "M", "question", 4),
    (6, 1, "题目编辑", "/question/edit", "QuestionEdit", "question:edit", "M", "edit", 5),
    (7, 1, "题目审核台", "/audit", "Audit", "question:audit", "M", "audit", 6),
    (8, 1, "批量导入", "/import", "Import", "question:import", "M", "import", 7),
    (9, 0, "组卷与练习", "/practice", None, None, "D", "paper", 2),
    (10, 9, "组卷工作台", "/paper/workbench", "PaperWorkbench", "paper:build", "M", "paper", 1),
    (11, 9, "试卷管理", "/paper", "PaperList", "paper:list", "M", "paper", 2),
    (12, 9, "练习中心", "/practice", "PracticeCenter", "practice:list", "M", "star", 3),
    (13, 9, "答题页", "/answer/:id", "Answer", "practice:answer", "M", "edit", 4),
    (14, 9, "我的错题本", "/wrong-book", "WrongBook", "wrong:list", "M", "question", 5),
    (15, 0, "学情诊断", "/mastery", None, None, "D", "radar", 3),
    (16, 15, "学情诊断", "/mastery", "Mastery", "mastery:view", "M", "radar", 1),
    (17, 15, "我的学情诊断", "/my-mastery", "MasteryStudent", "mastery:self", "M", "radar", 2),
    (18, 15, "班级学情", "/class-stat", "ClassStat", "mastery:class", "M", "chart", 3),
    (19, 15, "诊断规则配置", "/rule-config", "RuleConfig", "mastery:rule", "M", "rule", 4),
    (20, 0, "系统管理", "/system", None, None, "D", "user", 4),
    (21, 20, "用户与角色", "/system/user", "UserRole", "system:user", "M", "user", 1),
    (22, 20, "菜单管理", "/system/menu", "MenuList", "system:menu", "M", "tree", 2),
    (23, 20, "操作日志", "/system/log", "OperLog", "system:log", "M", "chart", 3),
    (24, 20, "公告与消息", "/system/notice", "NoticeList", "system:notice", "M", "bell", 4),
    (25, 20, "个人信息", "/profile", "Profile", "system:profile", "M", "user", 5),
]
w("INSERT INTO `sys_menu`(`id`,`parent_id`,`menu_name`,`path`,`component`,`perms`,`menu_type`,`icon`,`sort_no`,`visible`) VALUES\n" +
  ",\n".join(f"({a},{b},'{c}','{d}',{('NULL' if e is None else repr(e))},{('NULL' if f is None else repr(f))},'{g}','{h}',{i},1)"
            for a, b, c, d, e, f, g, h, i in MENUS) + ";")

# 角色菜单：管理员全部；教研员除系统管理；教师 首页+题库列表+组卷+试卷+班级学情；学生 门户页；秘书 统计+班级学情
rm = []
for mid in range(1, 26):
    rm.append((1, mid))
for mid in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 18, 19, 20, 24, 25]:
    rm.append((2, mid))
for mid in [1, 2, 5, 6, 9, 10, 11, 15, 18, 20, 25]:
    rm.append((3, mid))
for mid in [1, 2, 15, 18, 19, 20, 23, 24, 25]:
    rm.append((4, mid))
for mid in [9, 12, 13, 14, 15, 17, 20, 25]:
    rm.append((5, mid))
w("INSERT INTO `sys_role_menu`(`role_id`,`menu_id`) VALUES " + ",".join(f"({a},{b})" for a, b in rm) + ";")

# 公告 / 消息 / 日志 / 文件
w("""INSERT INTO `sys_notice`(`title`,`content`,`publish_time`,`status`,`create_by`,`create_time`) VALUES
('2026 春季学期期中测评安排','期中测评将于第 10 周进行，高等数学与数据结构采用在线组卷，请任课教师于第 9 周周五前完成试卷提交与审核。','2026-10-20 09:00:00',1,2,'2026-10-20 09:00:00'),
('题库新增《高等数学》积分章节 118 道题','教研组已完成积分章节题目入库，覆盖换元积分法、分部积分法与定积分应用，欢迎各位教师引用组卷。','2026-10-12 14:30:00',1,2,'2026-10-12 14:30:00'),
('关于校准知识点考纲权重的通知','请各学科负责人于 10 月 31 日前完成一级知识点权重核对，合计须等于 100，调整后系统将自动重算已发布试卷的覆盖度提示。','2026-10-05 10:15:00',1,1,'2026-10-05 10:15:00'),
('错题本复习计划功能上线','错题按 1 天、3 天、7 天生成复习计划，连续答对 2 次自动转为已掌握，请同学们及时完成到期复习。','2026-09-18 16:40:00',1,1,'2026-09-18 16:40:00');""")
w("""INSERT INTO `sys_message`(`receiver_id`,`title`,`content`,`biz_type`,`biz_id`,`read_flag`,`create_time`) VALUES
(2,'有 5 道题目待审核','高等数学与数据结构共 5 道题目等待您审核，其中 2 道已超过 24 小时。','QUESTION_AUDIT',0,4,'2026-10-31 09:12:00'),
(2,'试卷《大学物理 电磁学专项》待审核','任课教师周敏提交了试卷审核申请，请及时处理。','PAPER_AUDIT',5,0,'2026-10-31 08:40:00'),
(4,'您布置的练习已完成 32 人次','《高等数学 期中测评卷 A》当前完成率 76%，平均正确率 72.4%。','PRACTICE',1,1,'2026-10-30 20:00:00'),
(11,'今日有 4 道错题到期复习','换元积分法 2 道、二叉树遍历 1 道、定积分 1 道，请及时复习。','WRONG_REVIEW',0,0,'2026-11-01 06:00:00'),
(11,'《高等数学 期中测评卷 A》将于今晚截止','剩余时间不足 12 小时，您还有 11 道题未作答。','PRACTICE',1,0,'2026-11-01 06:05:00'),
(15,'您的掌握度诊断已更新','换元积分法掌握度由 38 升至 42，仍属严重薄弱，建议完成专项练习。','MASTERY',0,1,'2026-11-01 02:05:00'),
(6,'本月测评统计已生成','共 486 人次练习，平均正确率 72.4%，可导出明细报表。','STAT',0,1,'2026-10-31 18:20:00');""")
w("""INSERT INTO `sys_oper_log`(`module`,`oper_type`,`biz_no`,`content`,`oper_id`,`oper_name`,`oper_time`,`ip`) VALUES
('题目管理','审核','TM01000004','审核通过并入库，知识点归属：两个重要极限','2','李静','2026-10-30 14:22:00','127.0.0.1'),
('题目管理','审核','TM01000038','退回修改，原因：答案错误','2','李静','2026-10-29 10:08:00','127.0.0.1'),
('试卷管理','发布','SJ2604010001','发布并冻结 10 道题目快照','4','王振','2026-10-28 16:35:00','127.0.0.1'),
('知识点','权重调整','ZS0100012','换元积分法权重由 3.00 调整为 4.00','2','李静','2026-10-27 11:20:00','127.0.0.1'),
('掌握度','人工修正','MASTERY-2026-10-30','将换元积分法等级由严重薄弱修正为薄弱','2','李静','2026-10-30 09:14:00','127.0.0.1'),
('题库','批量导入','高数_第5章_积分.xlsx','导入 120 行，成功 118 行，失败 2 行','2','李静','2026-10-30 09:12:00','127.0.0.1'),
('练习','交卷','LX261030000012','自动判分完成，正确 7/10，得分 35.0','11','陈皓','2026-10-30 20:14:00','127.0.0.1');
""")
w("""INSERT INTO `sys_file`(`file_name`,`file_path`,`file_size`,`file_type`,`biz_type`,`biz_id`,`uploader_id`) VALUES
('avatar-01.jpg','/uploads/seed/avatar/01.jpg',182400,'jpg','avatar',1,1),
('figure-01.jpg','/uploads/seed/figure/01.jpg',214800,'jpg','question',1,4),
('高数_第5章_积分.xlsx','/uploads/import/202610/gaoshu-ch5.xlsx',48620,'xlsx','import',1,2);""")

# 冗余统计回填
w("""
-- ============ 统计字段回填（避免列表整列为 0） ============
UPDATE `subject` s SET s.`question_count` = (SELECT COUNT(*) FROM `question` q WHERE q.`subject_id` = s.`id` AND q.`status` = '已入库' AND q.`deleted` = 0);
UPDATE `knowledge_point` k SET k.`question_count` = (SELECT COUNT(*) FROM `question` q WHERE q.`knowledge_point_id` = k.`id` AND q.`status` = '已入库' AND q.`deleted` = 0);
UPDATE `question` q SET q.`correct_rate` = ROUND(
  100 * (SELECT IFNULL(SUM(a.`is_correct` = 1), 0) / NULLIF(COUNT(*), 0) FROM `practice_answer` a WHERE a.`question_id` = q.`id`), 2)
  WHERE EXISTS (SELECT 1 FROM `practice_answer` a2 WHERE a2.`question_id` = q.`id`);
UPDATE `question_option` o SET o.`chosen_count` = (SELECT COUNT(*) FROM `practice_answer` a WHERE a.`question_id` = o.`question_id` AND a.`user_answer` = o.`option_label`);
UPDATE `paper` p SET p.`question_count` = (SELECT COUNT(*) FROM `paper_question` pq WHERE pq.`paper_id` = p.`id` AND pq.`deleted` = 0)
  WHERE EXISTS (SELECT 1 FROM `paper_question` pq2 WHERE pq2.`paper_id` = p.`id`);
UPDATE `paper` p SET p.`total_score` = (SELECT IFNULL(SUM(pq.`score`), 0) FROM `paper_question` pq WHERE pq.`paper_id` = p.`id` AND pq.`deleted` = 0)
  WHERE EXISTS (SELECT 1 FROM `paper_question` pq3 WHERE pq3.`paper_id` = p.`id`);
UPDATE `paper` p SET p.`difficulty_avg` = ROUND((SELECT IFNULL(AVG(q.`difficulty`), 0.6) FROM `paper_question` pq JOIN `question` q ON q.`id` = pq.`question_id` WHERE pq.`paper_id` = p.`id`), 2)
  WHERE EXISTS (SELECT 1 FROM `paper_question` pq4 WHERE pq4.`paper_id` = p.`id`);
SET FOREIGN_KEY_CHECKS = 1;

-- 校验：各表行数
SELECT 'subject' t, COUNT(*) c FROM `subject` UNION ALL SELECT 'knowledge_point', COUNT(*) FROM `knowledge_point`
UNION ALL SELECT 'question', COUNT(*) FROM `question` UNION ALL SELECT 'question_option', COUNT(*) FROM `question_option`
UNION ALL SELECT 'paper', COUNT(*) FROM `paper` UNION ALL SELECT 'paper_question', COUNT(*) FROM `paper_question`
UNION ALL SELECT 'practice_record', COUNT(*) FROM `practice_record` UNION ALL SELECT 'practice_answer', COUNT(*) FROM `practice_answer`
UNION ALL SELECT 'wrong_book', COUNT(*) FROM `wrong_book` UNION ALL SELECT 'wrong_review_plan', COUNT(*) FROM `wrong_review_plan`
UNION ALL SELECT 'mastery_result', COUNT(*) FROM `mastery_result` UNION ALL SELECT 'mastery_rule', COUNT(*) FROM `mastery_rule`
UNION ALL SELECT 'question_audit', COUNT(*) FROM `question_audit` UNION ALL SELECT 'sys_menu', COUNT(*) FROM `sys_menu`
UNION ALL SELECT 'sys_user', COUNT(*) FROM `sys_user` UNION ALL SELECT 'sys_role_menu', COUNT(*) FROM `sys_role_menu`;
""")

OUT.write_text("\n".join(out), encoding="utf-8")
print("init.sql 生成完成，行数：", len("\n".join(out).splitlines()))
