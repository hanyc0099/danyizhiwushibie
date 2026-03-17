#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
历史记录API
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import pytz

from app.core.database import get_db, SessionLocal
from app.models.database import RecognitionHistory, Plant
from app.api.auth import get_current_user, SECRET_KEY, ALGORITHM
import jwt

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


class HistoryItem(BaseModel):
    """历史记录项"""
    id: int
    plant_id: int
    class_id: int
    plant_name: str
    confidence: float
    image_path: str
    is_favorite: bool
    created_at: str
    
    class Config:
        from_attributes = True


class SaveHistoryRequest(BaseModel):
    """保存历史记录请求"""
    user_id: Optional[str] = None
    plant_id: int
    class_id: int
    confidence: float
    plant_name: Optional[str] = None
    image_path: str
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    is_favorite: bool = False
    notes: Optional[str] = None


def _extract_user_id_from_token(credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[str]:
    """从Bearer token中提取user_id"""
    if credentials is None:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        return str(user_id) if user_id else None
    except Exception:
        return None


def _format_datetime(dt: datetime) -> str:
    """格式化日期时间为本地时间字符串"""
    if dt is None:
        return None
    # 转换为东八区时间
    tz = pytz.timezone('Asia/Shanghai')
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    local_dt = dt.astimezone(tz)
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")


@router.post("/save")
async def save_history(
    request: SaveHistoryRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    保存识别历史记录

    Args:
        request: 保存请求

    Returns:
        保存结果
    """
    # 优先从token提取user_id，其次使用请求体中的user_id
    token_user_id = _extract_user_id_from_token(credentials)
    user_id = token_user_id or request.user_id

    logger.info(f"[历史记录] 保存请求: plant_id={request.plant_id}, user_id={user_id}")
    
    db = SessionLocal()
    try:
        # 创建历史记录
        history = RecognitionHistory(
            user_id=user_id,
            plant_id=request.plant_id,
            class_id=request.class_id,
            confidence=request.confidence,
            plant_name=request.plant_name,
            image_path=request.image_path,
            latitude=request.latitude,
            longitude=request.longitude,
            is_favorite=1 if request.is_favorite else 0,
            notes=request.notes
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        logger.info(f"[历史记录] 保存成功: id={history.id}")
        
        return {
            "code": 200,
            "success": True,
            "message": "保存成功",
            "data": {
                "history_id": history.id,
                "created_at": _format_datetime(history.created_at)
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"[历史记录] 保存失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
    finally:
        db.close()


@router.get("/list")
async def get_history_list(
    user_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    获取历史记录列表

    Args:
        user_id: 用户ID（可选，为None则从token提取）
        page: 页码
        page_size: 每页数量

    Returns:
        历史记录列表
    """
    # 优先从token提取user_id
    token_user_id = _extract_user_id_from_token(credentials)
    effective_user_id = token_user_id or user_id

    logger.info(f"[历史记录] 查询列表: user_id={effective_user_id}, page={page}, page_size={page_size}")
    
    db = SessionLocal()
    try:
        # 构建查询
        query = db.query(RecognitionHistory)
        if effective_user_id:
            query = query.filter(RecognitionHistory.user_id == effective_user_id)
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        histories = query.order_by(RecognitionHistory.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为响应格式
        results = []
        for h in histories:
            # 查询植物信息 - 按 class_id 查询
            plant = db.query(Plant).filter(Plant.class_id == h.class_id).first()
            
            results.append({
                "id": h.id,
                "plant_id": h.plant_id,
                "class_id": h.class_id,
                "plant_name": h.plant_name or (plant.chinese_name if plant else f"植物{h.class_id}"),
                "confidence": h.confidence,
                "image_path": h.image_path,
                "image_url": h.image_path,
                "is_favorite": h.is_favorite == 1,
                "created_at": _format_datetime(h.created_at),
                "plant_image": plant.image_url if plant else None
            })
        
        return {
            "code": 200,
            "success": True,
            "message": f"共{total}条记录",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"[历史记录] 查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        db.close()


@router.get("/statistics")
async def get_history_statistics(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    获取识别统计信息
    
    Returns:
        今日识别数和累计识别数
    """
    # 从token提取user_id
    user_id = _extract_user_id_from_token(credentials)
    
    db = SessionLocal()
    try:
        from datetime import datetime, timedelta
        
        # 构建查询
        query = db.query(RecognitionHistory)
        if user_id:
            query = query.filter(RecognitionHistory.user_id == user_id)
        
        # 累计识别数
        total_count = query.count()
        
        # 今日识别数（按东八区时间统计，因为用户主要在中国）
        # 获取当前东八区时间
        tz = pytz.timezone('Asia/Shanghai')
        local_now = datetime.now(tz)
        local_today = local_now.date()
        # 转换为UTC时间进行查询
        local_today_start = tz.localize(datetime.combine(local_today, datetime.min.time()))
        local_today_end = tz.localize(datetime.combine(local_today, datetime.max.time()))
        utc_today_start = local_today_start.astimezone(pytz.utc).replace(tzinfo=None)
        utc_today_end = local_today_end.astimezone(pytz.utc).replace(tzinfo=None)
        
        today_query = query.filter(
            RecognitionHistory.created_at >= utc_today_start,
            RecognitionHistory.created_at <= utc_today_end
        )
        today_count = today_query.count()
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": {
                "today_count": today_count,
                "total_count": total_count
            }
        }
        
    except Exception as e:
        logger.error(f"[历史记录] 统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")
    finally:
        db.close()


@router.post("/{history_id}/favorite")
async def toggle_favorite(history_id: int):
    """
    切换收藏状态

    Args:
        history_id: 历史记录ID

    Returns:
        操作结果
    """
    db = SessionLocal()
    try:
        history = db.query(RecognitionHistory).filter(RecognitionHistory.id == history_id).first()
        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在")

        # 切换收藏状态
        history.is_favorite = 0 if history.is_favorite == 1 else 1
        db.commit()

        return {
            "code": 200,
            "success": True,
            "message": "操作成功",
            "data": {
                "is_favorite": history.is_favorite == 1
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[历史记录] 收藏操作失败: {e}")
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    finally:
        db.close()


@router.delete("/{history_id}")
async def delete_history(
    history_id: int,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    删除识别记录

    Args:
        history_id: 历史记录ID

    Returns:
        操作结果
    """
    # 从token提取user_id
    user_id = _extract_user_id_from_token(credentials)

    db = SessionLocal()
    try:
        query = db.query(RecognitionHistory).filter(RecognitionHistory.id == history_id)

        # 如果提供了user_id，则只能删除自己的记录
        if user_id:
            query = query.filter(RecognitionHistory.user_id == user_id)

        history = query.first()
        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在或无权删除")

        db.delete(history)
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
        logger.error(f"[历史记录] 删除失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        db.close()



