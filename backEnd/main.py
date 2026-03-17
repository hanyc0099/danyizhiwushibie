#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
植物识别后端服务
两阶段级联识别: YOLOv5n检测 + EfficientNet分类
"""

import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入配置
from app.core.config import load_config
from app.core.database import init_db

# 导入路由
from app.api import recognize, history, flowers, auth, posts, comments, upload
from app.api.auth import user_router

# 自定义JSON响应类，确保UTF-8编码
class UTF8JSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,  # 关键：不转义非ASCII字符
            indent=None,
            allow_nan=True,
            separators=(",", ":")
        ).encode('utf-8')

# 加载配置
config = load_config()

# 调试：打印配置结构
print("Config loaded")
print("   server keys: " + str(list(config['server'].keys())))

# 创建FastAPI应用
app = FastAPI(
    title="植物识别API",
    description="单一植物实时识别移动端后端服务 - YOLOv5n+EfficientNet两阶段级联识别",
    version="2.0.0",
    debug=config['server'].get('debug', True),
    default_response_class=UTF8JSONResponse
)

# 配置CORS
cors_config = config['server'].get('cors', {})
if cors_config.get('enabled', True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get('allow_origins', ["*"]),
        allow_credentials=cors_config.get('allow_credentials', True),
        allow_methods=cors_config.get('allow_methods', ["*"]),
        allow_headers=cors_config.get('allow_headers', ["*"]),
    )

# 注册路由
api_prefix = config['server'].get('api', {}).get('prefix', '/api/v1')
logger.info(f"🔧 API前缀: {api_prefix}")

# 识别路由
app.include_router(
    recognize.router,
    prefix=api_prefix,
    tags=["植物识别"]
)
logger.info(f"✅ 识别路由注册完成")

# 历史记录路由
app.include_router(
    history.router,
    prefix=f"{api_prefix}/history",
    tags=["历史记录"]
)
logger.info(f"✅ 历史记录路由注册完成")

# 植物信息路由
app.include_router(
    flowers.router,
    prefix=api_prefix,
    tags=["植物信息"]
)
logger.info(f"✅ 植物信息路由注册完成")

# 用户认证路由
app.include_router(
    auth.router,
    prefix=api_prefix,
    tags=["用户认证"]
)
logger.info(f"✅ 用户认证路由注册完成")

# 社区帖子路由
app.include_router(
    posts.router,
    prefix=api_prefix,
    tags=["社区帖子"]
)
logger.info(f"✅ 社区帖子路由注册完成")

# 用户相关帖子路由 (/user/posts)
app.include_router(
    posts.router,
    prefix=f"{api_prefix}/user",
    tags=["我的帖子"]
)
logger.info(f"✅ 用户帖子路由注册完成")

# 评论路由
app.include_router(
    comments.router,
    prefix=api_prefix,
    tags=["评论"]
)
logger.info(f"✅ 评论路由注册完成")

# 用户相关评论路由 (/user/comments)
app.include_router(
    comments.router,
    prefix=f"{api_prefix}/user",
    tags=["我的评论"]
)
logger.info(f"✅ 用户评论路由注册完成")

# 用户资料路由 (/user/info, /user/profile)
app.include_router(
    user_router,
    prefix=api_prefix,
    tags=["用户资料"]
)
logger.info(f"✅ 用户资料路由注册完成")

# 图片上传路由
app.include_router(
    upload.router,
    prefix=api_prefix,
    tags=["文件上传"]
)
logger.info(f"✅ 图片上传路由注册完成")

# 添加静态文件服务，提供uploads目录的访问
import os
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
    logger.info("✅ 静态文件服务已注册: /uploads")

dataset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
if os.path.exists(dataset_dir):
    app.mount("/dataset", StaticFiles(directory=dataset_dir), name="dataset")
    logger.info("✅ 静态文件服务已注册: /dataset")
else:
    logger.warning("⚠️ uploads目录不存在，无法提供静态文件服务")


@app.on_event("startup")
async def startup_event():
    """应用启动事件 - 初始化数据库和模型"""
    logger.info("=" * 60)
    logger.info("🌿 植物识别系统启动中...")
    logger.info("   版本: 2.0.0 (YOLOv5n + EfficientNet)")
    logger.info("=" * 60)
    
    # 初始化数据库
    try:
        logger.info("[启动] 初始化数据库...")
        init_db()
        logger.info("[启动] ✅ 数据库初始化完成")
    except Exception as e:
        logger.error(f"[启动] ⚠️ 数据库初始化失败: {e}")
    
    # 预加载识别模型
    try:
        from app.api.recognize import get_recognizer
        logger.info("[启动] 正在预加载识别模型...")
        recognizer = get_recognizer()
        if recognizer:
            logger.info("[启动] ✅ 识别模型预加载完成")
        else:
            logger.warning("[启动] ⚠️ 识别模型未加载")
    except Exception as e:
        logger.error(f"[启动] ⚠️ 模型预加载失败: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info(f"✅ 服务启动成功: http://{config['server'].get('host', '0.0.0.0')}:{config['server'].get('port', 8000)}")
    logger.info("=" * 60)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "植物识别系统API v2.0",
        "version": "2.0.0",
        "model": "YOLOv5n + EfficientNet-B0",
        "features": [
            "两阶段级联识别",
            "50种观赏植物",
            "SQLite本地存储"
        ],
        "endpoints": {
            "recognize": "/api/v1/recognize",
            "plants": "/api/v1/plants",
            "plant_detail": "/api/v1/plants/{id}",
            "history": "/api/v1/history/list",
            "health": "/api/v1/health"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    try:
        from app.api.recognize import get_recognizer
        recognizer = get_recognizer()
        
        return {
            "status": "healthy",
            "service": "plant-recognition-api",
            "version": "2.0.0",
            "model": "YOLOv5n + EfficientNet-B0",
            "database": "connected",
            "model_loaded": recognizer is not None,
            "num_classes": 50
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config['server'].get('host', '0.0.0.0'),
        port=config['server'].get('port', 8002),
        reload=config['server'].get('debug', True)
    )
