-- ============================================================
-- 花卉识别系统数据库创建脚本
-- 数据库: flower_recognition
-- 版本: 1.0
-- 创建日期: 2026-01-23
-- ============================================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS `flower_recognition` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `flower_recognition`;

-- ============================================================
-- 2. 创建用户表 (users)
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `openid` VARCHAR(64) NOT NULL COMMENT '微信OpenID',
  `unionid` VARCHAR(64) DEFAULT NULL COMMENT '微信UnionID',
  `nickname` VARCHAR(100) DEFAULT NULL COMMENT '用户昵称',
  `avatar_url` VARCHAR(500) DEFAULT NULL COMMENT '用户头像URL',
  `gender` TINYINT UNSIGNED DEFAULT NULL COMMENT '性别: 0-未知, 1-男, 2-女',
  `country` VARCHAR(50) DEFAULT NULL COMMENT '国家',
  `province` VARCHAR(50) DEFAULT NULL COMMENT '省份',
  `city` VARCHAR(50) DEFAULT NULL COMMENT '城市',
  `language` VARCHAR(20) DEFAULT 'zh_CN' COMMENT '语言',
  `status` TINYINT UNSIGNED DEFAULT 1 COMMENT '状态: 0-禁用, 1-正常',
  `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_openid` (`openid`),
  KEY `idx_unionid` (`unionid`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 3. 创建花卉表 (flowers)
-- ============================================================
CREATE TABLE IF NOT EXISTS `flowers` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '花卉ID',
  `class_id` INT UNSIGNED NOT NULL COMMENT '模型类别ID(对应模型输出的索引)',
  `english_name` VARCHAR(100) NOT NULL COMMENT '英文名称',
  `chinese_name` VARCHAR(100) NOT NULL COMMENT '中文名称',
  `scientific_name` VARCHAR(150) NOT NULL COMMENT '学名',
  `family` VARCHAR(50) DEFAULT NULL COMMENT '科名(中文)',
  `family_en` VARCHAR(50) DEFAULT NULL COMMENT '科名(英文)',
  `genus` VARCHAR(50) DEFAULT NULL COMMENT '属名(中文)',
  `genus_en` VARCHAR(50) DEFAULT NULL COMMENT '属名(英文)',
  `habits` TEXT COMMENT '生长习性',
  `description` TEXT COMMENT '详细描述',
  `characteristics` TEXT COMMENT '特征描述',
  `flowering_period` VARCHAR(100) DEFAULT NULL COMMENT '花期',
  `distribution` TEXT COMMENT '分布地区',
  `care_tips` TEXT COMMENT '养护建议',
  `image_url` VARCHAR(500) DEFAULT NULL COMMENT '示例图片URL',
  `status` TINYINT UNSIGNED DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_class_id` (`class_id`),
  KEY `idx_english_name` (`english_name`),
  KEY `idx_chinese_name` (`chinese_name`),
  KEY `idx_scientific_name` (`scientific_name`),
  KEY `idx_family` (`family`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='花卉表';

-- ============================================================
-- 4. 创建识别历史表 (recognition_history)
-- ============================================================
CREATE TABLE IF NOT EXISTS `recognition_history` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID',
  `flower_id` INT UNSIGNED NOT NULL COMMENT '花卉ID',
  `class_id` INT UNSIGNED NOT NULL COMMENT '模型类别ID',
  `confidence` DECIMAL(5,4) NOT NULL COMMENT '置信度(0-1)',
  `recognition_method` VARCHAR(50) NOT NULL COMMENT '识别方法: coze/local',
  `is_offline` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否离线识别: 0-否, 1-是',
  `image_url` VARCHAR(500) NOT NULL COMMENT '识别图片URL',
  `latitude` DECIMAL(10,7) DEFAULT NULL COMMENT '纬度',
  `longitude` DECIMAL(10,7) DEFAULT NULL COMMENT '经度',
  `location_detail` VARCHAR(200) DEFAULT NULL COMMENT '位置详情',
  `model_version` VARCHAR(50) DEFAULT NULL COMMENT '使用的模型版本',
  `top_k_results` JSON DEFAULT NULL COMMENT 'Top K预测结果(JSON格式)',
  `is_favorite` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否收藏: 0-否, 1-是',
  `notes` TEXT DEFAULT NULL COMMENT '用户备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_flower_id` (`flower_id`),
  KEY `idx_class_id` (`class_id`),
  KEY `idx_recognition_method` (`recognition_method`),
  KEY `idx_is_offline` (`is_offline`),
  KEY `idx_is_favorite` (`is_favorite`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_location` (`latitude`, `longitude`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='识别历史表';

-- ============================================================
-- 5. 创建用户收藏表 (user_collections)
-- ============================================================
CREATE TABLE IF NOT EXISTS `user_collections` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '收藏ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `flower_id` INT UNSIGNED NOT NULL COMMENT '花卉ID',
  `history_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '关联的历史记录ID',
  `notes` TEXT DEFAULT NULL COMMENT '收藏备注',
  `tags` VARCHAR(200) DEFAULT NULL COMMENT '标签(逗号分隔)',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_flower_history` (`user_id`, `flower_id`, `history_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_flower_id` (`flower_id`),
  KEY `idx_history_id` (`history_id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表';

-- ============================================================
-- 6. 创建模型版本表 (model_versions)
-- ============================================================
CREATE TABLE IF NOT EXISTS `model_versions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '版本ID',
  `version_name` VARCHAR(50) NOT NULL COMMENT '版本号(如: v1.0, v2.0)',
  `model_type` VARCHAR(50) NOT NULL COMMENT '模型类型: resnet50/mobilenetv3',
  `model_file` VARCHAR(200) NOT NULL COMMENT '模型文件路径',
  `onnx_file` VARCHAR(200) NOT NULL COMMENT 'ONNX模型文件路径',
  `labels_file` VARCHAR(200) NOT NULL COMMENT '标签文件路径',
  `num_classes` INT UNSIGNED NOT NULL COMMENT '类别数量',
  `accuracy` DECIMAL(5,4) NOT NULL COMMENT '准确率(0-1)',
  `inference_time_ms` INT UNSIGNED DEFAULT NULL COMMENT '平均推理时间(毫秒)',
  `model_size_mb` DECIMAL(10,2) DEFAULT NULL COMMENT '模型大小(MB)',
  `training_epochs` INT UNSIGNED DEFAULT NULL COMMENT '训练轮数',
  `training_data_size` INT UNSIGNED DEFAULT NULL COMMENT '训练数据量',
  `is_active` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否激活使用: 0-否, 1-是',
  `is_public` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否公开: 0-否, 1-是',
  `description` TEXT DEFAULT NULL COMMENT '模型描述',
  `created_by` VARCHAR(50) DEFAULT NULL COMMENT '创建者',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_version_name` (`version_name`),
  KEY `idx_model_type` (`model_type`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型版本表';

-- ============================================================
-- 7. 创建系统配置表 (system_config)
-- ============================================================
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键',
  `config_value` TEXT NOT NULL COMMENT '配置值',
  `config_type` VARCHAR(20) DEFAULT 'string' COMMENT '配置类型: string/number/boolean/json',
  `description` VARCHAR(200) DEFAULT NULL COMMENT '配置描述',
  `is_public` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否公开: 0-否, 1-是',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`),
  KEY `idx_is_public` (`is_public`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 插入当前模型版本信息
INSERT INTO `model_versions` (`version_name`, `model_type`, `model_file`, `onnx_file`, `labels_file`, `num_classes`, `accuracy`, `inference_time_ms`, `model_size_mb`, `training_epochs`, `training_data_size`, `is_active`, `description`) VALUES
('v1.0', 'resnet50', '../models/flower_20class_resnet50_best.pth', '../models/flower_20class_resnet50.onnx', '../models/flower_20class_resnet50_labels.json', 21, 0.9835, 450, 98.5, 31, 871, 1, 'ResNet50模型，支持21种花卉识别，训练准确率98.35%');

-- 插入系统配置
INSERT INTO `system_config` (`config_key`, `config_value`, `config_type`, `description`, `is_public`) VALUES
('recognition.default_method', 'coze', 'string', '默认识别方法: coze/local', 1),
('recognition.auto_fallback', 'true', 'boolean', '在线识别失败时是否自动降级到本地模型', 1),
('recognition.confidence_threshold', '0.5', 'number', '识别置信度阈值', 0),
('recognition.top_k', '3', 'number', '返回Top K预测结果数量', 1),
('recognition.enable_coze', 'true', 'boolean', '是否启用Coze在线识别', 0),
('recognition.enable_local', 'true', 'boolean', '是否启用本地模型识别', 1),
('image.max_size_mb', '10', 'number', '上传图片最大尺寸(MB)', 1),
('image.allow_formats', 'jpg,jpeg,png', 'string', '允许的图片格式', 1),
('history.page_size', '20', 'number', '历史记录每页显示数量', 1);

-- ============================================================
-- 9. 创建索引优化查询性能
-- ============================================================

-- 复合索引优化常用查询
CREATE INDEX `idx_history_user_created` ON `recognition_history` (`user_id`, `created_at` DESC);
CREATE INDEX `idx_history_flower_created` ON `recognition_history` (`flower_id`, `created_at` DESC);
CREATE INDEX `idx_history_offline_created` ON `recognition_history` (`is_offline`, `created_at` DESC);
CREATE INDEX `idx_collection_user_created` ON `user_collections` (`user_id`, `created_at` DESC);
