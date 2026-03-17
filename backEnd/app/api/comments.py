#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
评论API接口
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import Comment, User
from app.api.auth import get_current_user

router = APIRouter()


class CommentCreate(BaseModel):
    """创建评论请求"""
    plant_id: Optional[int] = None
    post_id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str


class CommentResponse(BaseModel):
    """评论响应"""
    id: int
    user_id: int
    plant_id: int
    parent_id: Optional[int]
    content: str
    likes: int
    dislikes: int
    is_adopted: bool
    created_at: str
    user: Optional[dict] = None
    plant_name: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("")
async def get_comments(
    plant_id: int = 0,
    post_id: int = 0,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取评论列表

    Args:
        plant_id: 植物ID（0表示获取所有评论）
        post_id: 帖子ID（0表示获取所有评论）
        page: 页码
        page_size: 每页数量
        db: 数据库会话

    Returns:
        评论列表
    """
    try:
        query = db.query(Comment).filter(Comment.is_deleted == False)
        
        if plant_id > 0:
            query = query.filter(Comment.plant_id == plant_id)
        
        if post_id > 0:
            query = query.filter(Comment.post_id == post_id)
        
        # 只获取顶级评论（没有parent_id的）
        query = query.filter(Comment.parent_id == None)
        
        # 按时间倒序
        query = query.order_by(Comment.created_at.desc())
        
        # 分页
        total = query.count()
        offset = (page - 1) * page_size
        comments = query.offset(offset).limit(page_size).all()
        
        # 构建响应
        result = []
        for comment in comments:
            comment_data = {
                "id": comment.id,
                "user_id": comment.user_id,
                "post_id": comment.post_id,
                "plant_id": comment.plant_id,
                "parent_id": comment.parent_id,
                "content": comment.content,
                "likes": comment.likes,
                "dislikes": comment.dislikes,
                "is_adopted": comment.is_adopted,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M") if comment.created_at else "",
            }
            
            # 获取用户信息
            user = db.query(User).filter(User.id == comment.user_id).first()
            if user:
                comment_data["user"] = {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "avatar_url": user.avatar_url
                }
            
            # 获取植物名称
            from app.models.database import Plant
            if comment.plant_id:
                plant = db.query(Plant).filter(Plant.id == comment.plant_id).first()
                if plant:
                    comment_data["plant_name"] = plant.chinese_name
            
            result.append(comment_data)
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": {
                "comments": result,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取评论失败: {str(e)}"
        )


@router.post("")
async def add_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加评论

    Args:
        comment_data: 评论数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        添加的评论
    """
    try:
        # 验证必须指定 plant_id 或 post_id 之一
        if not comment_data.plant_id and not comment_data.post_id:
            raise HTTPException(status_code=400, detail="必须指定 plant_id 或 post_id")
        
        new_comment = Comment(
            user_id=current_user.id,
            plant_id=comment_data.plant_id,
            post_id=comment_data.post_id,
            parent_id=comment_data.parent_id,
            content=comment_data.content,
            likes=0,
            dislikes=0,
            is_adopted=False,
            created_at=datetime.now()
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # 如果是对帖子的评论，更新帖子的评论数
        if comment_data.post_id:
            from app.models.database import Post
            post = db.query(Post).filter(Post.id == comment_data.post_id).first()
            if post:
                post.comments_count += 1
                db.commit()
        
        # 构建返回数据，包含用户信息
        result = {
            "id": new_comment.id,
            "user_id": new_comment.user_id,
            "post_id": new_comment.post_id,
            "plant_id": new_comment.plant_id,
            "parent_id": new_comment.parent_id,
            "content": new_comment.content,
            "likes": new_comment.likes,
            "dislikes": new_comment.dislikes,
            "is_adopted": new_comment.is_adopted,
            "created_at": new_comment.created_at.strftime("%Y-%m-%d %H:%M"),
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "nickname": current_user.nickname,
                "avatar_url": current_user.avatar_url
            }
        }
        
        # 获取植物名称
        if comment_data.plant_id:
            from app.models.database import Plant
            plant = db.query(Plant).filter(Plant.id == comment_data.plant_id).first()
            if plant:
                result["plant_name"] = plant.chinese_name
        
        return {
            "code": 200,
            "success": True,
            "message": "评论成功",
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"评论失败: {str(e)}"
        )


@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    点赞评论

    Args:
        comment_id: 评论ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        点赞结果
    """
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        comment.likes += 1
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "点赞成功",
            "data": {"likes": comment.likes}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"点赞失败: {str(e)}"
        )


@router.post("/comments/{comment_id}/dislike")
async def dislike_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    踩评论

    Args:
        comment_id: 评论ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        踩结果
    """
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        comment.dislikes += 1
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "已踩",
            "data": {"dislikes": comment.dislikes}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"操作失败: {str(e)}"
        )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除评论（软删除）

    Args:
        comment_id: 评论ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        # 只能删除自己的评论
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除")
        
        comment.is_deleted = True
        db.commit()
        
        # 如果是对帖子的评论，更新帖子的评论数
        if comment.post_id:
            from app.models.database import Post
            post = db.query(Post).filter(Post.id == comment.post_id).first()
            if post:
                post.comments_count = max(0, post.comments_count - 1)
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
        raise HTTPException(
            status_code=500,
            detail=f"删除失败: {str(e)}"
        )


class CommentUpdate(BaseModel):
    """更新评论请求"""
    content: str


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新评论

    Args:
        comment_id: 评论ID
        update_data: 更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新结果
    """
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id, Comment.is_deleted == False).first()
        if not comment:
            raise HTTPException(status_code=404, detail="评论不存在")
        
        # 只能编辑自己的评论
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权编辑")
        
        comment.content = update_data.content
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "更新成功",
            "data": {
                "id": comment.id,
                "content": comment.content
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"更新失败: {str(e)}"
        )


@router.get("/my")
async def get_my_comments(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取我的评论列表

    Args:
        page: 页码
        page_size: 每页数量
        current_user: 当前用户
        db: 数据库会话

    Returns:
        评论列表
    """
    try:
        query = db.query(Comment).filter(
            Comment.user_id == current_user.id,
            Comment.is_deleted == False
        ).order_by(Comment.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * page_size
        comments = query.offset(offset).limit(page_size).all()
        
        result = []
        for comment in comments:
            comment_data = {
                "id": comment.id,
                "post_id": comment.post_id,
                "plant_id": comment.plant_id,
                "content": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content,
                "likes": comment.likes,
                "dislikes": comment.dislikes,
                "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M") if comment.created_at else ""
            }
            
            # 获取帖子标题
            if comment.post_id:
                from app.models.database import Post
                post = db.query(Post).filter(Post.id == comment.post_id).first()
                if post:
                    comment_data["post_title"] = post.title
            
            result.append(comment_data)
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": {
                "comments": result,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取失败: {str(e)}"
        )
