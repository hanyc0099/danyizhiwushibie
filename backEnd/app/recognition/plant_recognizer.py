#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
植物识别服务 - 两阶段级联架构
第一阶段: YOLOv5n 检测植物区域
第二阶段: EfficientNet-B0 分类识别
"""

import os
import io
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image

import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

# 尝试导入YOLOv5
import sys
yolo_path = Path(__file__).parent.parent.parent / "yolov5"
if str(yolo_path) not in sys.path:
    sys.path.insert(0, str(yolo_path))

try:
    from models.common import DetectMultiBackend
    from utils.general import non_max_suppression, scale_boxes
    from utils.torch_utils import select_device
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("YOLOv5未安装，将使用直接分类模式")

logger = logging.getLogger(__name__)


class PlantRecognizer:
    """植物识别器 - YOLOv5n检测 + EfficientNet分类"""
    
    def __init__(self, 
                 detector_path: str = None,
                 classifier_path: str = None,
                 num_classes: int = 50):
        """
        初始化识别器
        
        Args:
            detector_path: YOLOv5n检测模型路径 (.pt或.onnx)
            classifier_path: EfficientNet分类模型路径 (.pt)
            num_classes: 分类类别数
        """
        self.num_classes = num_classes
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"[初始化] 植物识别器")
        logger.info(f"  设备: {self.device}")
        logger.info(f"  类别数: {num_classes}")
        
        # 加载检测器
        self.detector = self._load_detector(detector_path)
        
        # 加载分类器
        self.classifier = self._load_classifier(classifier_path)
        
        # 加载类别标签
        self.class_names = self._load_class_names()
        
        # 图像预处理
        self.detector_transform = self._get_detector_transform()
        self.classifier_transform = self._get_classifier_transform()
        
    def _load_detector(self, model_path: str) -> Optional[torch.nn.Module]:
        """加载YOLOv5n检测器"""
        if not YOLO_AVAILABLE or model_path is None:
            logger.warning("  检测器未加载，将使用整图分类")
            return None
        
        try:
            logger.info(f"  加载检测器: {model_path}")
            device = select_device(str(self.device))
            model = DetectMultiBackend(model_path, device=device, dnn=False)
            
            # 设置推理尺寸
            self.detector_stride = model.stride
            self.detector_img_size = 640
            
            logger.info(f"  [OK] 检测器加载成功")
            return model
        except Exception as e:
            logger.error(f"  [错误] 检测器加载失败: {e}")
            return None
    
    def _load_classifier(self, model_path: str) -> torch.nn.Module:
        """加载EfficientNet-B0分类器"""
        logger.info(f"  加载分类器...")
        
        # 创建模型
        model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        
        # 修改分类层
        num_features = model.classifier[1].in_features
        model.classifier[1] = torch.nn.Linear(num_features, self.num_classes)
        
        # 加载自定义权重
        if model_path and os.path.exists(model_path):
            logger.info(f"    加载权重: {model_path}")
            checkpoint = torch.load(model_path, map_location=self.device)
            if 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)
            logger.info(f"    [OK] 自定义权重加载成功")
        else:
            logger.warning(f"    未找到权重文件，使用预训练权重进行特征提取")
        
        model = model.to(self.device)
        model.eval()
        
        logger.info(f"  [OK] 分类器加载成功")
        return model
    
    def _load_class_names(self) -> List[str]:
        """加载类别名称"""
        # 50种观赏植物名称列表
        class_names = [
            "绿萝", "吊兰", "虎尾兰", "龟背竹", "发财树",
            "橡皮树", "琴叶榕", "富贵竹", "文竹", "铜钱草",
            "豆瓣绿", "常春藤", "绿萝藤", "一叶兰", "万年青",
            "月季", "茉莉花", "栀子花", "杜鹃花", "蝴蝶兰",
            "君子兰", "长寿花", "蟹爪兰", "仙客来", "天竺葵",
            "绣球花", "康乃馨", "百合", "郁金香", "风信子",
            "水仙", "红掌", "白掌", "三角梅", "菊花",
            "芦荟", "仙人掌", "多肉组合", "生石花", "玉露",
            "熊童子", "吉娃娃", "虹之玉", "法师", "锦晃星",
            "薄荷", "迷迭香", "薰衣草", "铁线蕨", "空气凤梨"
        ]
        return class_names
    
    def _get_detector_transform(self):
        """检测器图像预处理"""
        return transforms.Compose([
            transforms.Resize((640, 640)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def _get_classifier_transform(self):
        """分类器图像预处理"""
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def detect(self, image: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """
        检测植物区域
        
        Args:
            image: PIL图像
            
        Returns:
            bbox: (x1, y1, x2, y2) 或 None
        """
        if self.detector is None:
            return None
        
        try:
            # 保存原始尺寸
            orig_width, orig_height = image.size
            
            # 预处理
            img_tensor = self.detector_transform(image).unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                pred = self.detector(img_tensor)
                
                # NMS
                pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)
            
            # 处理结果
            if len(pred) > 0 and pred[0] is not None and len(pred[0]) > 0:
                # 取置信度最高的检测框
                det = pred[0][0].cpu().numpy()
                
                # 缩放到原图尺寸
                x1, y1, x2, y2 = det[:4]
                x1 = int(x1 * orig_width / 640)
                y1 = int(y1 * orig_height / 640)
                x2 = int(x2 * orig_width / 640)
                y2 = int(y2 * orig_height / 640)
                
                # 边界检查
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(orig_width, x2)
                y2 = min(orig_height, y2)
                
                return (x1, y1, x2, y2)
            
            return None
            
        except Exception as e:
            logger.error(f"检测失败: {e}")
            return None
    
    def classify(self, image: Image.Image) -> List[Dict]:
        """
        分类识别
        
        Args:
            image: PIL图像
            
        Returns:
            分类结果列表，每项包含class_id, name, confidence
        """
        try:
            # 预处理
            img_tensor = self.classifier_transform(image).unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                outputs = self.classifier(img_tensor)
                probabilities = F.softmax(outputs, dim=1)
            
            # 获取Top-5结果
            probs, indices = torch.topk(probabilities[0], k=5)
            
            results = []
            for i, (prob, idx) in enumerate(zip(probs, indices)):
                class_id = idx.item()
                confidence = prob.item()
                name = self.class_names[class_id] if class_id < len(self.class_names) else f"未知{class_id}"
                
                results.append({
                    'class_id': class_id,
                    'name': name,
                    'confidence': confidence,
                    'rank': i + 1
                })
            
            return results
            
        except Exception as e:
            logger.error(f"分类失败: {e}")
            return []
    
    def recognize(self, image_data: bytes, top_k: int = 5) -> Dict:
        """
        完整识别流程
        
        Args:
            image_data: 图像字节数据
            top_k: 返回前k个结果
            
        Returns:
            识别结果字典
        """
        logger.info(f"[识别请求] 图像大小: {len(image_data)} bytes")
        
        try:
            # 加载图像
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            orig_width, orig_height = image.size
            logger.info(f"  图像尺寸: {orig_width}x{orig_height}")
            
            # 第一阶段: 检测植物区域
            bbox = self.detect(image)
            
            if bbox:
                x1, y1, x2, y2 = bbox
                logger.info(f"  检测到植物区域: ({x1}, {y1}, {x2}, {y2})")
                
                # 裁剪ROI区域
                roi_image = image.crop(bbox)
            else:
                logger.info(f"  未检测到植物区域，使用整图")
                roi_image = image
            
            # 第二阶段: 分类识别
            results = self.classify(roi_image)
            
            # 限制返回数量
            results = results[:top_k]
            
            logger.info(f"  [识别结果] Top {len(results)}:")
            for r in results:
                logger.info(f"    {r['rank']}. {r['name']} - {r['confidence']*100:.2f}%")
            
            return {
                'success': True,
                'bbox': bbox,
                'results': results,
                'image_size': (orig_width, orig_height)
            }
            
        except Exception as e:
            logger.error(f"识别失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'results': []
            }


# 全局单例
_recognizer = None


def get_recognizer() -> PlantRecognizer:
    """获取识别器单例"""
    global _recognizer
    if _recognizer is None:
        # 模型路径
        base_path = Path(__file__).parent.parent.parent
        detector_path = base_path / "models" / "yolov5n_plant.pt"
        classifier_path = base_path / "models" / "efficientnet_b0_plant.pt"
        
        _recognizer = PlantRecognizer(
            detector_path=str(detector_path) if detector_path.exists() else None,
            classifier_path=str(classifier_path) if classifier_path.exists() else None
        )
    return _recognognizer
