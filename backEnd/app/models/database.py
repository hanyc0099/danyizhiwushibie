#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库模型 - SQLite
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(50), unique=True, nullable=False, comment='用户名')
    password = Column(String(255), nullable=False, comment='密码哈希')
    nickname = Column(String(100), comment='昵称')
    avatar_url = Column(String(500), comment='头像URL')
    bio = Column(String(500), comment='个人简介')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    last_login_at = Column(DateTime, comment='最后登录时间')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login_at': self.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_at else None
        }


class Post(Base):
    """帖子表"""
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='帖子ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    history_id = Column(Integer, comment='关联的识别历史ID')
    plant_id = Column(Integer, comment='关联的植物ID')
    title = Column(String(200), comment='帖子标题')
    content = Column(Text, nullable=False, comment='帖子内容')
    image_urls = Column(Text, comment='图片URL列表(JSON)')
    post_type = Column(String(20), default='share', comment='类型: share/correction/experience')
    likes = Column(Integer, default=0, comment='点赞数')
    favorites = Column(Integer, default=0, comment='收藏数')
    comments_count = Column(Integer, default=0, comment='评论数')
    is_deleted = Column(Boolean, default=False, comment='是否删除')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'history_id': self.history_id,
            'plant_id': self.plant_id,
            'title': self.title,
            'content': self.content,
            'post_type': self.post_type,
            'likes': self.likes,
            'favorites': self.favorites,
            'comments_count': self.comments_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


class Comment(Base):
    """评论表"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='评论ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    post_id = Column(Integer, comment='帖子ID')
    plant_id = Column(Integer, comment='植物ID')
    parent_id = Column(Integer, comment='父评论ID')
    content = Column(Text, nullable=False, comment='评论内容')
    likes = Column(Integer, default=0, comment='点赞数')
    dislikes = Column(Integer, default=0, comment='踩数')
    is_adopted = Column(Boolean, default=False, comment='是否被采纳')
    is_deleted = Column(Boolean, default=False, comment='是否删除')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'plant_id': self.plant_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'likes': self.likes,
            'dislikes': self.dislikes,
            'is_adopted': self.is_adopted,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


class PostLike(Base):
    """帖子点赞表"""
    __tablename__ = 'post_likes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PostFavorite(Base):
    """帖子收藏表"""
    __tablename__ = 'post_favorites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Plant(Base):
    """植物信息表"""
    __tablename__ = 'plants'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='植物ID，自增主键')
    
    # 分类标识
    class_id = Column(Integer, nullable=False, unique=True, comment='模型类别ID，对应模型输出的索引(0-49)')
    
    # 基本信息
    chinese_name = Column(String(100), nullable=False, comment='中文名称')
    english_name = Column(String(100), comment='英文名称')
    scientific_name = Column(String(150), comment='拉丁学名')
    
    # 分类信息
    family = Column(String(50), comment='科名(中文)')
    genus = Column(String(50), comment='属名(中文)')
    
    # 特征描述
    description = Column(Text, comment='植物详细描述')
    characteristics = Column(Text, comment='形态特征')
    flowering_period = Column(String(100), comment='花期')
    
    # 养护信息
    care_tips = Column(Text, comment='养护建议(浇水、光照、施肥等)')
    difficulty_level = Column(Integer, default=2, comment='养护难度: 1-简单, 2-中等, 3-困难')
    
    # 图片信息
    image_url = Column(String(500), comment='示例图片URL或本地路径')
    
    # 状态管理
    status = Column(Integer, default=1, comment='状态: 0-禁用, 1-启用')
    view_count = Column(Integer, default=0, comment='浏览次数')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'chinese_name': self.chinese_name,
            'english_name': self.english_name,
            'scientific_name': self.scientific_name,
            'family': self.family,
            'genus': self.genus,
            'description': self.description,
            'characteristics': self.characteristics,
            'flowering_period': self.flowering_period,
            'care_tips': self.care_tips,
            'difficulty_level': self.difficulty_level,
            'image_url': self.image_url,
            'status': self.status,
            'view_count': self.view_count
        }


class RecognitionHistory(Base):
    """识别历史表"""
    __tablename__ = 'recognition_history'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='记录ID，自增主键')
    
    # 关联信息（不使用外键约束）
    plant_id = Column(Integer, comment='关联的植物ID(plants表)')
    class_id = Column(Integer, nullable=False, comment='识别的类别ID')
    
    # 识别结果
    confidence = Column(Float, nullable=False, comment='置信度(0-1之间)')
    plant_name = Column(String(100), comment='识别的植物名称(冗余存储，方便查询)')
    
    # 图片信息
    image_path = Column(String(500), nullable=False, comment='识别的图片本地存储路径')
    
    # 位置信息（可选）
    latitude = Column(Float, comment='纬度')
    longitude = Column(Float, comment='经度')
    location_name = Column(String(200), comment='位置描述')
    
    # 用户标识（支持游客模式）
    user_id = Column(String(64), comment='用户ID或设备标识')
    
    # 收藏标记
    is_favorite = Column(Integer, default=0, comment='是否收藏: 0-否, 1-是')
    notes = Column(Text, comment='用户备注')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='识别时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'plant_id': self.plant_id,
            'class_id': self.class_id,
            'confidence': self.confidence,
            'plant_name': self.plant_name,
            'image_path': self.image_path,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'user_id': self.user_id,
            'is_favorite': self.is_favorite,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_database(db_path: str = "plant_recognition.db"):
    """
    初始化数据库
    
    Args:
        db_path: 数据库文件路径
    """
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session_maker(engine):
    """获取会话工厂"""
    return sessionmaker(bind=engine)
