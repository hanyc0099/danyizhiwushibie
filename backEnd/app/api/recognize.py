#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
植物识别API接口 - 高级识别 (YOLOv10 + EfficientNet+CBAM)
"""

import os
import io
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from PIL import Image

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 导入数据库
from app.core.database import get_db, SessionLocal
from app.models.database import Plant

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局识别器实例（延迟加载）
_recognizer = None
_feature_matcher = None
_use_advanced = True  # 是否使用高级识别器


def get_recognizer():
    """获取或创建识别器实例（单例模式）"""
    global _recognizer
    if _recognizer is None:
        try:
            if _use_advanced:
                # 使用高级识别器 (YOLOv10 + EfficientNet+CBAM)
                from app.recognition.advanced_plant_recognizer import AdvancedPlantRecognizer
                
                base_path = Path(__file__).parent.parent.parent
                detector_path = base_path / "models" / "yolov10n.pt"
                classifier_path = base_path / "models" / "efficientnet_cbam_50class.pth"
                
                logger.info(f"[模型路径] YOLOv10检测器: {detector_path}, 存在: {detector_path.exists()}")
                logger.info(f"[模型路径] EfficientNet+CBAM: {classifier_path}, 存在: {classifier_path.exists()}")
                
                _recognizer = AdvancedPlantRecognizer(
                    detector_path=str(detector_path) if detector_path.exists() else None,
                    classifier_path=str(classifier_path) if classifier_path.exists() else None,
                    num_classes=50  # 50类植物
                )
                logger.info("[OK] 高级植物识别器初始化成功 (YOLOv10 + EfficientNet+CBAM)")
            else:
                # 使用基础识别器 (YOLOv5 + EfficientNet)
                from app.recognition.plant_recognizer import PlantRecognizer
                
                base_path = Path(__file__).parent.parent.parent
                detector_path = base_path / "models" / "yolov5n.pt"
                classifier_path = base_path / "models" / "efficientnet_b0_2class.pth"
                
                logger.info(f"[模型路径] 检测器: {detector_path}, 存在: {detector_path.exists()}")
                logger.info(f"[模型路径] 分类器: {classifier_path}, 存在: {classifier_path.exists()}")
                
                _recognizer = PlantRecognizer(
                    detector_path=str(detector_path) if detector_path.exists() else None,
                    classifier_path=str(classifier_path) if classifier_path.exists() else None,
                    num_classes=2
                )
                logger.info("[OK] 基础植物识别器初始化成功")
                
        except Exception as e:
            logger.error(f"[错误] 识别器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            _recognizer = None
    return _recognizer


def get_feature_matcher():
    """获取或创建特征匹配器实例（单例模式）"""
    global _feature_matcher
    if _feature_matcher is None:
        try:
            from app.recognition.feature_matcher import FeatureMatcher
            
            base_path = Path(__file__).parent.parent.parent
            dataset_path = base_path / "dataset"
            
            logger.info(f"[特征匹配器] 数据集路径: {dataset_path}")
            
            _feature_matcher = FeatureMatcher(dataset_dir=str(dataset_path))
            logger.info("[OK] 特征匹配器初始化成功")
        except Exception as e:
            logger.error(f"[错误] 特征匹配器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            _feature_matcher = None
    return _feature_matcher


class RecognitionResult(BaseModel):
    """识别结果"""
    class_id: int
    plant_id: int
    chinese_name: str
    confidence: float
    scientific_name: Optional[str] = None
    family: Optional[str] = None
    genus: Optional[str] = None
    description: Optional[str] = None
    care_tips: Optional[str] = None


class RecognitionResponse(BaseModel):
    """识别响应"""
    code: int
    success: bool
    message: str
    data: List[RecognitionResult]


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_plant(
    image: UploadFile = File(..., description="植物图片"),
    latitude: float = Form(0.0, description="纬度"),
    longitude: float = Form(0.0, description="经度"),
    top_k: int = Form(5, description="返回前k个结果", ge=1, le=10)
):
    """
    识别植物图片
    
    采用两阶段级联架构:
    1. YOLOv5n检测植物区域
    2. EfficientNet-B0分类识别
    
    Args:
        image: 上传的植物图片
        latitude: 识别位置的纬度（可选）
        longitude: 识别位置的经度（可选）
        top_k: 返回前k个识别结果（1-10）
        
    Returns:
        识别结果列表，按置信度排序
    """
    logger.info(f"[API] 收到识别请求: {image.filename}, 位置: ({latitude}, {longitude})")
    
    try:
        # 获取识别器
        recognizer = get_recognizer()
        if recognizer is None:
            raise HTTPException(status_code=503, detail="识别服务初始化失败")
        
        # 读取图片数据
        image_data = await image.read()
        logger.info(f"  图片大小: {len(image_data)} bytes")
        
        # 执行识别
        result = recognizer.recognize(image_data, top_k=top_k)
        
        if not result['success']:
            logger.error(f"  识别失败: {result.get('error', '未知错误')}")
            raise HTTPException(status_code=500, detail=result.get('error', '识别失败'))
        
        # 查询数据库获取详细信息
        db = next(get_db())
        try:
            recognition_results = []
            
            for rec in result['results']:
                class_id = rec['class_id']
                confidence = rec['confidence']
                
                # 从数据库查询植物信息
                plant = db.query(Plant).filter(Plant.class_id == class_id).first()
                
                if plant:
                    recognition_results.append(RecognitionResult(
                        class_id=class_id,
                        plant_id=plant.id,
                        chinese_name=plant.chinese_name,
                        confidence=confidence,
                        scientific_name=plant.scientific_name,
                        family=plant.family,
                        genus=plant.genus,
                        description=plant.description,
                        care_tips=plant.care_tips
                    ))
                else:
                    # 使用默认信息
                    recognition_results.append(RecognitionResult(
                        class_id=class_id,
                        plant_id=0,
                        chinese_name=rec['name'],
                        confidence=confidence
                    ))
            
            logger.info(f"  [OK] 识别成功，返回 {len(recognition_results)} 个结果")
            
            return RecognitionResponse(
                code=200,
                success=True,
                message="识别成功",
                data=recognition_results
            )
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"  [错误] 识别异常: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")


@router.get("/plants", response_model=Dict)
async def get_plants_list():
    """获取所有植物列表"""
    db = SessionLocal()
    try:
        plants = db.query(Plant).filter(Plant.status == 1).all()
        
        return {
            "code": 200,
            "success": True,
            "message": f"共{len(plants)}种植物",
            "data": [
                {
                    "id": p.id,
                    "class_id": p.class_id,
                    "chinese_name": p.chinese_name,
                    "english_name": p.english_name,
                    "scientific_name": p.scientific_name,
                    "family": p.family,
                    "genus": p.genus,
                    "image_url": p.image_url
                }
                for p in plants
            ]
        }
    finally:
        db.close()


@router.get("/plants/{plant_id}", response_model=Dict)
async def get_plant_detail(plant_id: int):
    """获取植物详细信息
    
    Args:
        plant_id: 植物ID（class_id，模型类别ID 0-49）
    """
    db = SessionLocal()
    try:
        # 按 class_id 查询（模型类别ID 0-49）
        plant = db.query(Plant).filter(Plant.class_id == plant_id).first()
        
        if not plant:
            raise HTTPException(status_code=404, detail="植物不存在")
        
        return {
            "code": 200,
            "success": True,
            "message": "获取成功",
            "data": {
                "id": plant.id,
                "class_id": plant.class_id,
                "chinese_name": plant.chinese_name,
                "english_name": plant.english_name,
                "scientific_name": plant.scientific_name,
                "family": plant.family,
                "genus": plant.genus,
                "description": plant.description,
                "characteristics": plant.characteristics,
                "flowering_period": plant.flowering_period,
                "care_tips": plant.care_tips,
                "difficulty_level": plant.difficulty_level,
                "image_url": plant.image_url,
                "view_count": plant.view_count
            }
        }
    finally:
        db.close()


@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        recognizer = get_recognizer()
        
        status = {
            "code": 200,
            "success": True,
            "message": "服务正常",
            "data": {
                "model_loaded": recognizer is not None,
                "detector_loaded": recognizer.detector is not None if recognizer else False,
                "classifier_loaded": recognizer.classifier is not None if recognizer else False,
                "num_classes": recognizer.num_classes if recognizer else 0,
                "device": str(recognizer.device) if recognizer else "unknown"
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "code": 503,
            "success": False,
            "message": f"服务异常: {str(e)}"
        }
