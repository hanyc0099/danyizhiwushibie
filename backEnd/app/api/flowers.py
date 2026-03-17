#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
植物信息API
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.database import Plant

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/plants")
async def get_plants_list(
    family: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """
    获取植物列表
    
    Args:
        family: 按科筛选
        keyword: 关键词搜索
        page: 页码
        page_size: 每页数量
        
    Returns:
        植物列表
    """
    db = SessionLocal()
    try:
        query = db.query(Plant).filter(Plant.status == 1)
        
        # 按科筛选
        if family:
            query = query.filter(Plant.family == family)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                Plant.chinese_name.contains(keyword) |
                Plant.english_name.contains(keyword) |
                Plant.scientific_name.contains(keyword)
            )
        
        # 计算总数
        total = query.count()
        
        # 分页查询
        plants = query.order_by(Plant.class_id).offset((page - 1) * page_size).limit(page_size).all()
        
        return {
            "code": 200,
            "success": True,
            "message": f"共{total}种植物",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": [p.to_dict() for p in plants]
            }
        }
        
    except Exception as e:
        logger.error(f"[植物信息] 查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        db.close()


@router.get("/plants/{plant_id}")
async def get_plant_detail(plant_id: int):
    """
    获取植物详情
    
    Args:
        plant_id: 植物ID（class_id，模型类别ID 0-49）
        
    Returns:
        植物详细信息
    """
    db = SessionLocal()
    try:
        # 按 class_id 查询（模型类别ID 0-49）
        plant = db.query(Plant).filter(Plant.class_id == plant_id).first()
        
        if not plant:
            raise HTTPException(status_code=404, detail="植物不存在")
        
        # 增加浏览次数
        plant.view_count = (plant.view_count or 0) + 1
        db.commit()
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": plant.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[植物信息] 查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        db.close()


@router.get("/families")
async def get_families():
    """
    获取所有科分类
    
    Returns:
        科分类列表
    """
    db = SessionLocal()
    try:
        families = db.query(Plant.family).filter(
            Plant.status == 1,
            Plant.family != None
        ).distinct().all()
        
        return {
            "code": 200,
            "success": True,
            "message": f"共{len(families)}个科",
            "data": [f[0] for f in families if f[0]]
        }
        
    except Exception as e:
        logger.error(f"[植物信息] 查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    finally:
        db.close()
