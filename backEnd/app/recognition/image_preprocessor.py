#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图像预处理模块
提供灰度化、降噪、尺寸归一化、增强等功能
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """植物图像预处理器"""
    
    def __init__(self, target_size: Tuple[int, int] = (640, 640)):
        """
        初始化预处理器
        
        Args:
            target_size: 目标输出尺寸 (宽, 高)
        """
        self.target_size = target_size
        logger.info(f"[ImagePreprocessor] 初始化完成，目标尺寸: {target_size}")
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        完整预处理流程
        
        Args:
            image: 输入图像 (BGR格式)
            
        Returns:
            预处理后的图像
        """
        logger.info("[预处理] 开始图像预处理...")
        
        # 1. 灰度化
        if len(image.shape) == 3:
            gray = self.to_grayscale(image)
        else:
            gray = image.copy()
        logger.info("  [1/5] 灰度化完成")
        
        # 2. 降噪
        denoised = self.denoise(gray)
        logger.info("  [2/5] 降噪完成")
        
        # 3. 图像增强
        enhanced = self.enhance(denoised)
        logger.info("  [3/5] 增强完成")
        
        # 4. 转回RGB
        rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        logger.info("  [4/5] 转RGB完成")
        
        # 5. 尺寸归一化
        normalized = self.normalize_size(rgb)
        logger.info("  [5/5] 尺寸归一化完成")
        
        return normalized
    
    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        灰度化 - 使用加权平均法
        
        Args:
            image: 彩色图像 (BGR格式)
            
        Returns:
            灰度图像
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def denoise(self, image: np.ndarray, method: str = "gaussian") -> np.ndarray:
        """
        降噪处理
        
        Args:
            image: 输入图像
            method: 降噪方法 ("gaussian", "median", "bilateral")
            
        Returns:
            降噪后的图像
        """
        if method == "gaussian":
            return cv2.GaussianBlur(image, (5, 5), 0)
        elif method == "median":
            return cv2.medianBlur(image, 5)
        elif method == "bilateral":
            return cv2.bilateralFilter(image, 9, 75, 75)
        else:
            return image
    
    def enhance(self, image: np.ndarray) -> np.ndarray:
        """
        图像增强 - 包括CLAHE和锐化
        
        Args:
            image: 输入图像
            
        Returns:
            增强后的图像
        """
        # 自适应直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # 锐化
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
    
    def normalize_size(self, image: np.ndarray) -> np.ndarray:
        """
        尺寸归一化 - 保持长宽比，居中填充
        
        Args:
            image: 输入图像
            
        Returns:
            归一化后的图像
        """
        h, w = image.shape[:2]
        target_w, target_h = self.target_size
        
        # 计算缩放比例
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # 缩放
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # 创建画布并居中放置
        if len(image.shape) == 3:
            result = np.full((target_h, target_w, 3), 128, dtype=np.uint8)
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        else:
            result = np.full((target_h, target_w), 128, dtype=np.uint8)
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            result[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return result


def preprocess_for_classification(image: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    为分类模型预处理图像
    
    Args:
        image: 输入图像 (BGR格式)
        target_size: 目标尺寸
        
    Returns:
        预处理后的图像 (RGB格式)
    """
    # 转RGB
    if len(image.shape) == 3:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    # 缩放
    resized = cv2.resize(rgb, target_size, interpolation=cv2.INTER_LANCZOS4)
    
    return resized


if __name__ == '__main__':
    # 测试
    print("测试图像预处理模块...")
    
    # 创建测试图像
    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    preprocessor = ImagePreprocessor(target_size=(640, 640))
    result = preprocessor.preprocess(test_img)
    
    print(f"输入: {test_img.shape}")
    print(f"输出: {result.shape}")
    print("✅ 测试通过!")
