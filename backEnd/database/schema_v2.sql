-- ============================================================
-- 植物识别系统数据库建表脚本
-- 数据库: plant_recognition
-- 版本: 2.0
-- 说明: 毕设项目简化版，包含毒性预警功能
-- ============================================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS `plant_recognition` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `plant_recognition`;

-- ============================================================
-- 2. 用户表 (users)
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `password` VARCHAR(255) NOT NULL COMMENT '密码(BCrypt加密)',
  `nickname` VARCHAR(100) DEFAULT NULL COMMENT '昵称',
  `avatar_url` VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_login_at` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================================
-- 3. 植物信息表 (plants)
-- ============================================================
CREATE TABLE IF NOT EXISTS `plants` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '植物ID',
  `class_id` INT UNSIGNED NOT NULL COMMENT '模型类别ID(对应CLIP模型输出索引)',
  `chinese_name` VARCHAR(100) NOT NULL COMMENT '中文名称',
  `scientific_name` VARCHAR(150) DEFAULT NULL COMMENT '学名',
  `family` VARCHAR(50) DEFAULT NULL COMMENT '科名',
  `description` TEXT COMMENT '详细描述(包含习性、分布等)',
  `image_url` VARCHAR(500) DEFAULT NULL COMMENT '示例图片URL',
  
  -- 毒性相关字段
  `toxicity_level` VARCHAR(20) DEFAULT 'safe' COMMENT '毒性等级: safe-安全无毒/low-微毒/high-剧毒',
  `toxic_parts` TEXT COMMENT '有毒部位(多个用逗号分隔)',
  `toxicity_symptoms` TEXT COMMENT '中毒症状描述',
  `emergency_advice` TEXT COMMENT '急救建议',
  
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_class_id` (`class_id`),
  KEY `idx_toxicity` (`toxicity_level`),
  KEY `idx_chinese_name` (`chinese_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='植物信息表';

-- ============================================================
-- 4. 识别历史表 (recognition_history)
-- ============================================================
CREATE TABLE IF NOT EXISTS `recognition_history` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID',
  `plant_id` INT UNSIGNED NOT NULL COMMENT '植物ID',
  `class_id` INT UNSIGNED NOT NULL COMMENT '模型类别ID',
  `confidence` DECIMAL(5,4) NOT NULL COMMENT '置信度(0-1)',
  `image_url` VARCHAR(500) NOT NULL COMMENT '识别图片URL',
  `latitude` DECIMAL(10,7) DEFAULT NULL COMMENT '纬度',
  `longitude` DECIMAL(10,7) DEFAULT NULL COMMENT '经度',
  `location_detail` VARCHAR(200) DEFAULT NULL COMMENT '位置详情',
  `is_favorite` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否收藏: 0-否, 1-是',
  `notes` TEXT DEFAULT NULL COMMENT '用户备注',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_plant_id` (`plant_id`),
  KEY `idx_is_favorite` (`is_favorite`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='识别历史表';

-- ============================================================
-- 5. 插入示例植物数据(含毒性信息)
-- ============================================================

-- 剧毒植物示例
INSERT INTO `plants` (`class_id`, `chinese_name`, `scientific_name`, `family`, `description`, `toxicity_level`, `toxic_parts`, `toxicity_symptoms`, `emergency_advice`) VALUES
(1, '海芋', 'Alocasia odora', '天南星科', '多年生草本，叶片大，呈箭形。常生于阴湿环境、林下、溪边。分布于华南、西南地区。', 'high', '块茎、汁液、叶片', '口腔麻木、咽喉肿痛、呕吐、腹泻、严重者可致窒息', '立即停止食用，不要催吐，立即就医！携带植物样本'),
(2, '夹竹桃', 'Nerium oleander', '夹竹桃科', '常绿灌木，花色有红、白、粉等。常见于路边、公园绿化。全株有毒，燃烧烟雾亦有毒性。', 'high', '全株(叶、花、茎、根、汁液)', '恶心、呕吐、腹痛、腹泻、心律失常、严重者可致死', '立即就医！不要催吐！告知医生可能夹竹桃中毒'),
(3, '曼陀罗', 'Datura stramonium', '茄科', '一年生草本，花白色喇叭状，果实有刺。生于荒地、路旁。全株有毒，种子毒性最强。', 'high', '全株(种子、花、叶、根)', '口干、瞳孔散大、幻觉、谵妄、昏迷、呼吸抑制', '立即就医！保持呼吸道通畅，不要催吐'),
(4, '断肠草', 'Gelsemium elegans', '马钱科', '常绿藤本，花黄色。生于山地疏林中。全株剧毒，根和叶毒性最强。', 'high', '全株(根、叶、花、茎)', '眩晕、恶心、肌肉松弛、呼吸麻痹、可致死', '立即就医！人工呼吸，保持呼吸道通畅'),
(5, '毒芹', 'Cicuta virosa', '伞形科', '多年生草本，形似芹菜。生于水边、沼泽。全株剧毒，根茎毒性最强。', 'high', '全株(根茎毒性最强)', '恶心、呕吐、抽搐、呼吸麻痹、可致死', '立即就医！不要催吐，保持呼吸道通畅');

-- 微毒植物示例
INSERT INTO `plants` (`class_id`, `chinese_name`, `scientific_name`, `family`, `description`, `toxicity_level`, `toxic_parts`, `toxicity_symptoms`, `emergency_advice`) VALUES
(6, '水仙', 'Narcissus tazetta', '石蒜科', '多年生草本，花白色或黄色，芳香。常见于水边、庭院。鳞茎有毒，误食可中毒。', 'low', '鳞茎', '恶心、呕吐、腹痛、腹泻', '多喝水，症状严重就医'),
(7, '郁金香', 'Tulipa gesneriana', '百合科', '多年生草本，花色丰富。常见于公园、花坛。接触汁液可能致敏。', 'low', '鳞茎、汁液', '接触皮肤可致红肿瘙痒，误食可致恶心呕吐', '避免接触汁液，误食后多喝水'),
(8, '滴水观音', 'Alocasia macrorrhizos', '天南星科', '多年生草本，叶片大。常见于室内盆栽。汁液有毒，接触皮肤可致瘙痒。', 'low', '汁液、叶片', '皮肤接触可致红肿瘙痒，误食可致口腔麻木', '避免接触汁液，误食后漱口就医'),
(9, '绿萝', 'Epipremnum aureum', '天南星科', '常绿藤本，叶片心形。常见室内盆栽。汁液有微毒，接触皮肤可致瘙痒。', 'low', '汁液', '皮肤接触可致红肿瘙痒，误食可致口腔不适', '避免接触汁液，误食后漱口'),
(10, '一品红', 'Euphorbia pulcherrima', '大戟科', '灌木，顶部叶片红色。常见于圣诞装饰。汁液有微毒。', 'low', '汁液、叶片', '皮肤接触可致红肿，误食可致恶心呕吐腹泻', '避免接触汁液，误食后多喝水');

-- 安全植物示例
INSERT INTO `plants` (`class_id`, `chinese_name`, `scientific_name`, `family`, `description`, `toxicity_level`, `toxic_parts`, `toxicity_symptoms`, `emergency_advice`) VALUES
(11, '玫瑰', 'Rosa rugosa', '蔷薇科', '落叶灌木，花色丰富，芳香。喜阳光充足，耐寒耐旱。全国各地均有栽培。', 'safe', NULL, NULL, NULL),
(12, '茉莉花', 'Jasminum sambac', '木犀科', '常绿灌木，花白色芳香。喜温暖湿润，常见于南方庭院。花可泡茶。', 'safe', NULL, NULL, NULL),
(13, '桂花', 'Osmanthus fragrans', '木犀科', '常绿乔木，花黄色或白色，芳香。喜温暖，常见于南方。花可食用、制茶。', 'safe', NULL, NULL, NULL),
(14, '向日葵', 'Helianthus annuus', '菊科', '一年生草本，花盘大，黄色。喜阳光，全国各地均有种植。种子可食用。', 'safe', NULL, NULL, NULL),
(15, '薰衣草', 'Lavandula angustifolia', '唇形科', '多年生草本，花紫色，芳香。喜阳光干燥。可用于香料、精油。', 'safe', NULL, NULL, NULL);

-- ============================================================
-- 6. 创建索引优化查询
-- ============================================================
CREATE INDEX `idx_history_user_created` ON `recognition_history` (`user_id`, `created_at` DESC);
CREATE INDEX `idx_history_plant_created` ON `recognition_history` (`plant_id`, `created_at` DESC);
