-- 社区帖子功能数据库迁移脚本
-- 执行时间: 2026-03-02

-- 1. 添加用户 bio 字段
ALTER TABLE users ADD COLUMN bio VARCHAR(500) COMMENT '个人简介' AFTER avatar_url;

-- 2. 创建评论表
CREATE TABLE IF NOT EXISTS comments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    post_id BIGINT COMMENT '帖子ID',
    plant_id INT COMMENT '植物ID',
    parent_id BIGINT COMMENT '父评论ID(回复)',
    content TEXT NOT NULL COMMENT '评论内容',
    likes INT DEFAULT 0 COMMENT '点赞数',
    dislikes INT DEFAULT 0 COMMENT '点踩数',
    is_adopted BOOLEAN DEFAULT FALSE COMMENT '是否被采纳',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_post_id (post_id),
    INDEX idx_plant_id (plant_id),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- 3. 创建帖子表
CREATE TABLE IF NOT EXISTS posts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '帖子ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    history_id BIGINT COMMENT '识别记录ID',
    plant_id INT COMMENT '植物ID',
    title VARCHAR(200) COMMENT '标题',
    content TEXT NOT NULL COMMENT '内容',
    image_urls TEXT COMMENT '图片URL列表，JSON格式',
    likes INT DEFAULT 0 COMMENT '点赞数',
    favorites INT DEFAULT 0 COMMENT '收藏数',
    comments_count INT DEFAULT 0 COMMENT '评论数',
    post_type VARCHAR(20) DEFAULT 'share' COMMENT '帖子类型: share/correction/experience',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_history_id (history_id),
    INDEX idx_plant_id (plant_id),
    INDEX idx_post_type (post_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子表';

-- 4. 创建帖子点赞表
CREATE TABLE IF NOT EXISTS post_likes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    post_id BIGINT NOT NULL COMMENT '帖子ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY unique_user_post_like (user_id, post_id),
    INDEX idx_post_id (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子点赞表';

-- 5. 创建帖子收藏表
CREATE TABLE IF NOT EXISTS post_favorites (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    post_id BIGINT NOT NULL COMMENT '帖子ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY unique_user_post_favorite (user_id, post_id),
    INDEX idx_post_id (post_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子收藏表';
