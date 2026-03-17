#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片上传API
处理图片上传并返回可访问的URL
"""

import os
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# 图片存储目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
IMAGE_DIR = os.path.join(UPLOAD_DIR, "images")

# 确保目录存在
os.makedirs(IMAGE_DIR, exist_ok=True)

# 允许的图片格式
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename.lower())[1]


def is_allowed_file(filename: str) -> bool:
    """检查文件是否允许上传"""
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片文件
    
    Args:
        file: 图片文件
        
    Returns:
        图片访问URL
    """
    logger.info(f"[上传] 接收到图片上传请求: {file.filename}")
    
    # 检查文件名
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 检查文件类型
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式，只允许: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # 读取文件内容
        content = await file.read()
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"文件大小超过限制，最大允许: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # 生成唯一文件名
        ext = get_file_extension(file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = os.path.join(IMAGE_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 生成访问URL
        image_url = f"/uploads/images/{unique_filename}"
        
        logger.info(f"[上传] 图片保存成功: {file_path}")
        
        return {
            "code": 200,
            "success": True,
            "message": "上传成功",
            "data": {
                "url": image_url,
                "filename": unique_filename,
                "size": len(content)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[上传] 保存图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/uploads/images/{filename}")
async def get_image(filename: str):
    """
    获取上传的图片
    
    Args:
        filename: 图片文件名
        
    Returns:
        图片文件
    """
    file_path = os.path.join(IMAGE_DIR, filename)
    
    # 安全检查：确保文件在指定目录内
    real_path = os.path.realpath(file_path)
    real_image_dir = os.path.realpath(IMAGE_DIR)
    
    if not real_path.startswith(real_image_dir):
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    
    # 根据扩展名确定媒体类型
    ext = get_file_extension(filename)
    media_type = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp'
    }.get(ext, 'application/octet-stream')
    
    return FileResponse(file_path, media_type=media_type)
