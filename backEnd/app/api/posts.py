#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
帖子API接口
"""

import logging
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import Post, Comment, User, Plant, RecognitionHistory, PostLike, PostFavorite
from app.api.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["社区帖子"])
logger = logging.getLogger(__name__)


class PostCreate(BaseModel):
    """创建帖子请求"""
    history_id: Optional[int] = None
    plant_id: Optional[int] = None
    title: Optional[str] = None
    content: str
    image_urls: Optional[List[str]] = []
    post_type: str = "share"  # share, correction, experience


class PostUpdate(BaseModel):
    """更新帖子请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    image_urls: Optional[List[str]] = None


@router.post("/create")
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建帖子"""
    try:
        # 如果有 history_id，验证记录存在
        if post_data.history_id:
            history = db.query(RecognitionHistory).filter(
                RecognitionHistory.id == post_data.history_id,
                RecognitionHistory.user_id == current_user.id
            ).first()
            if not history:
                raise HTTPException(status_code=404, detail="识别记录不存在")
        
        # 创建帖子
        new_post = Post(
            user_id=current_user.id,
            history_id=post_data.history_id,
            plant_id=post_data.plant_id,
            title=post_data.title,
            content=post_data.content,
            image_urls=json.dumps(post_data.image_urls) if post_data.image_urls else "[]",
            post_type=post_data.post_type,
            created_at=datetime.now()
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return {
            "code": 200,
            "success": True,
            "message": "发布成功",
            "data": {"post_id": new_post.id}
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")


@router.get("")
async def get_posts(
    page: int = 1,
    page_size: int = 20,
    post_type: Optional[str] = None,
    plant_id: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取帖子列表"""
    try:
        query = db.query(Post).filter(Post.is_deleted == False)
        
        if post_type:
            query = query.filter(Post.post_type == post_type)
        if plant_id:
            query = query.filter(Post.plant_id == plant_id)
        
        # 按时间倒序
        query = query.order_by(Post.created_at.desc())
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        posts = query.offset(offset).limit(page_size).all()
        
        # 构建响应
        result = []
        for post in posts:
            # 获取用户信息
            user = db.query(User).filter(User.id == post.user_id).first()
            
            post_data = {
                "id": post.id,
                "user_id": post.user_id,
                "history_id": post.history_id,
                "plant_id": post.plant_id,
                "title": post.title,
                "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                "image_urls": json.loads(post.image_urls) if post.image_urls else [],
                "likes": post.likes,
                "favorites": post.favorites,
                "comments_count": post.comments_count,
                "post_type": post.post_type,
                "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
                "user": {
                    "id": user.id if user else post.user_id,
                    "username": user.username if user else "",
                    "nickname": user.nickname if user else "",
                    "avatar_url": user.avatar_url if user else ""
                },
                "is_liked": False,
                "is_favorited": False
            }
            
            # 获取植物名称
            if post.plant_id:
                plant = db.query(Plant).filter(Plant.id == post.plant_id).first()
                if plant:
                    post_data["plant_name"] = plant.chinese_name
            
            # 检查当前用户是否点赞/收藏
            if current_user:
                is_liked = db.query(PostLike).filter(
                    PostLike.user_id == current_user.id,
                    PostLike.post_id == post.id
                ).first() is not None
                
                is_favorited = db.query(PostFavorite).filter(
                    PostFavorite.user_id == current_user.id,
                    PostFavorite.post_id == post.id
                ).first() is not None
                
                post_data["is_liked"] = is_liked
                post_data["is_favorited"] = is_favorited
            
            result.append(post_data)
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": {
                "posts": result,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/{post_id}")
async def get_post_detail(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取帖子详情"""
    try:
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在")
        
        # 获取用户信息
        user = db.query(User).filter(User.id == post.user_id).first()
        
        # 获取评论列表
        comments = db.query(Comment).filter(
            Comment.post_id == post_id,
            Comment.is_deleted == False
        ).order_by(Comment.created_at.desc()).limit(20).all()
        
        comments_data = []
        for comment in comments:
            comment_user = db.query(User).filter(User.id == comment.user_id).first()
            comments_data.append({
                "id": comment.id,
                "user_id": comment.user_id,
                "content": comment.content,
                "likes": comment.likes,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
                "user": {
                    "id": comment_user.id if comment_user else comment.user_id,
                    "nickname": comment_user.nickname if comment_user else "",
                    "avatar_url": comment_user.avatar_url if comment_user else ""
                }
            })
        
        result = {
            "id": post.id,
            "user_id": post.user_id,
            "history_id": post.history_id,
            "plant_id": post.plant_id,
            "title": post.title,
            "content": post.content,
            "image_urls": json.loads(post.image_urls) if post.image_urls else [],
            "likes": post.likes,
            "favorites": post.favorites,
            "comments_count": post.comments_count,
            "post_type": post.post_type,
            "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
            "user": {
                "id": user.id if user else post.user_id,
                "username": user.username if user else "",
                "nickname": user.nickname if user else "",
                "avatar_url": user.avatar_url if user else ""
            },
            "comments": comments_data,
            "is_liked": False,
            "is_favorited": False
        }
        
        # 获取植物名称
        if post.plant_id:
            plant = db.query(Plant).filter(Plant.id == post.plant_id).first()
            if plant:
                result["plant_name"] = plant.chinese_name
        
        # 检查当前用户是否点赞/收藏
        if current_user:
            is_liked = db.query(PostLike).filter(
                PostLike.user_id == current_user.id,
                PostLike.post_id == post_id
            ).first() is not None
            
            is_favorited = db.query(PostFavorite).filter(
                PostFavorite.user_id == current_user.id,
                PostFavorite.post_id == post_id
            ).first() is not None
            
            result["is_liked"] = is_liked
            result["is_favorited"] = is_favorited
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """点赞/取消点赞帖子"""
    try:
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在")
        
        # 检查是否已点赞
        existing_like = db.query(PostLike).filter(
            PostLike.user_id == current_user.id,
            PostLike.post_id == post_id
        ).first()
        
        if existing_like:
            # 取消点赞
            db.delete(existing_like)
            post.likes = max(0, post.likes - 1)
            is_liked = False
        else:
            # 添加点赞
            new_like = PostLike(user_id=current_user.id, post_id=post_id)
            db.add(new_like)
            post.likes += 1
            is_liked = True
        
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "取消点赞" if not is_liked else "点赞成功",
            "data": {"likes": post.likes, "is_liked": is_liked}
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.post("/{post_id}/favorite")
async def favorite_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """收藏/取消收藏帖子"""
    try:
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在")
        
        # 检查是否已收藏
        existing_favorite = db.query(PostFavorite).filter(
            PostFavorite.user_id == current_user.id,
            PostFavorite.post_id == post_id
        ).first()
        
        if existing_favorite:
            # 取消收藏
            db.delete(existing_favorite)
            post.favorites = max(0, post.favorites - 1)
            is_favorited = False
        else:
            # 添加收藏
            new_favorite = PostFavorite(user_id=current_user.id, post_id=post_id)
            db.add(new_favorite)
            post.favorites += 1
            is_favorited = True
        
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "取消收藏" if not is_favorited else "收藏成功",
            "data": {"favorites": post.favorites, "is_favorited": is_favorited}
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除帖子（软删除）"""
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在")
        
        # 只能删除自己的帖子
        if post.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除")
        
        post.is_deleted = True
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.put("/{post_id}")
async def update_post(
    post_id: int,
    update_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新帖子"""
    try:
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="帖子不存在")
        
        # 只能编辑自己的帖子
        if post.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权编辑")
        
        if update_data.title is not None:
            post.title = update_data.title
        if update_data.content is not None:
            post.content = update_data.content
        if update_data.image_urls is not None:
            post.image_urls = json.dumps(update_data.image_urls)
        
        post.updated_at = datetime.now()
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "更新成功",
            "data": post.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.get("/my")
async def get_my_posts(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的帖子列表"""
    try:
        query = db.query(Post).filter(
            Post.user_id == current_user.id,
            Post.is_deleted == False
        ).order_by(Post.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * page_size
        posts = query.offset(offset).limit(page_size).all()
        
        result = []
        for post in posts:
            post_data = {
                "id": post.id,
                "title": post.title,
                "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                "image_urls": json.loads(post.image_urls) if post.image_urls else [],
                "likes": post.likes,
                "favorites": post.favorites,
                "comments_count": post.comments_count,
                "post_type": post.post_type,
                "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "nickname": current_user.nickname,
                    "avatar_url": current_user.avatar_url
                }
            }
            result.append(post_data)
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": {
                "posts": result,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/my/favorites")
async def get_my_favorites(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我收藏的帖子列表"""
    try:
        query = db.query(PostFavorite).filter(
            PostFavorite.user_id == current_user.id
        ).order_by(PostFavorite.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * page_size
        favorites = query.offset(offset).limit(page_size).all()
        
        result = []
        for fav in favorites:
            post = db.query(Post).filter(Post.id == fav.post_id, Post.is_deleted == False).first()
            if post:
                user = db.query(User).filter(User.id == post.user_id).first()
                result.append({
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                    "image_urls": json.loads(post.image_urls) if post.image_urls else [],
                    "likes": post.likes,
                    "favorites": post.favorites,
                    "comments_count": post.comments_count,
                    "post_type": post.post_type,
                    "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
                    "user": {
                        "id": user.id if user else post.user_id,
                        "nickname": user.nickname if user else "",
                        "avatar_url": user.avatar_url if user else ""
                    }
                })
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": {
                "posts": result,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
