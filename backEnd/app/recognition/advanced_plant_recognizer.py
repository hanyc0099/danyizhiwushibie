#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高级植物识别器 v2.0
集成:
- 图像预处理 (灰度化、降噪、增强)
- YOLOv10 检测
- EfficientNet + CBAM 分类
"""

import os
import io
import cv2
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from .image_preprocessor import ImagePreprocessor, preprocess_for_classification
from .cbam import EfficientNetWithCBAM
from .class_mapping import get_db_class_id

logger = logging.getLogger(__name__)


class AdvancedPlantRecognizer:
    """高级植物识别器 - YOLOv10检测 + EfficientNet+CBAM分类"""
    
    def __init__(self, 
                 detector_path: str = None,
                 classifier_path: str = None,
                 num_classes: int = 50,
                 device: str = None):
        """
        初始化识别器
        
        Args:
            detector_path: YOLOv10检测模型路径
            classifier_path: EfficientNet+CBAM分类模型路径
            num_classes: 分类类别数
            device: 计算设备
        """
        self.num_classes = num_classes
        self.device = torch.device(device if device else ('cuda' if torch.cuda.is_available() else 'cpu'))
        self.classifier_path = classifier_path
        
        logger.info("="*60)
        logger.info("[初始化] 高级植物识别器 v2.0")
        logger.info(f"  设备: {self.device}")
        logger.info(f"  类别数: {num_classes}")
        
        # 初始化图像预处理器
        self.preprocessor = ImagePreprocessor(target_size=(640, 640))
        logger.info("  [OK] 图像预处理器初始化完成")
        
        # 加载检测器 (YOLOv10)
        self.detector = self._load_detector(detector_path)
        
        # 加载分类器 (EfficientNet+CBAM)
        self.classifier = self._load_classifier(classifier_path)
        
        # 加载类别标签（从模型文件加载）
        self.class_names = self._load_class_names()
        
        logger.info("="*60)
    
    def _load_detector(self, detector_path: str) -> Optional[torch.nn.Module]:
        """加载YOLOv10检测器"""
        if not detector_path or not Path(detector_path).exists():
            logger.warning(f"  检测器路径不存在: {detector_path}")
            return None
        
        logger.info(f"  加载YOLOv10检测器...")
        try:
            # 直接使用ultralytics YOLO加载
            from ultralytics import YOLO
            model = YOLO(detector_path)
            model.to(self.device)
            logger.info(f"    [OK] YOLOv10检测器加载成功")
            return model
        except Exception as e:
            logger.error(f"    [错误] YOLOv10加载失败: {e}")
            logger.warning(f"    将不使用检测器，直接使用整图分类")
            return None
    
    def _load_classifier(self, classifier_path: str) -> Optional[torch.nn.Module]:
        """加载EfficientNet+CBAM分类器"""
        logger.info(f"  加载EfficientNet+CBAM分类器...")
        
        try:
            # 创建模型
            model = EfficientNetWithCBAM(num_classes=self.num_classes, pretrained=True)
            model = model.to(self.device)
            
            # 加载自定义权重
            if classifier_path and Path(classifier_path).exists():
                checkpoint = torch.load(classifier_path, map_location=self.device)
                if 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                    logger.info(f"    [OK] 自定义权重加载成功")
                else:
                    model.load_state_dict(checkpoint)
                    logger.info(f"    [OK] 权重加载成功")
            else:
                logger.warning(f"    未找到权重文件，使用预训练权重")
            
            model.eval()
            logger.info(f"  [OK] 分类器加载成功")
            return model
            
        except Exception as e:
            logger.error(f"  [错误] 分类器加载失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_class_names(self) -> List[str]:
        """加载类别名称 - 从模型文件加载"""
        # 首先尝试从模型文件加载类别名称
        if self.classifier_path and Path(self.classifier_path).exists():
            try:
                checkpoint = torch.load(self.classifier_path, map_location='cpu')
                if 'class_names' in checkpoint:
                    class_names = checkpoint['class_names']
                    logger.info(f"  [OK] 从模型加载 {len(class_names)} 个类别名称")
                    return class_names
            except Exception as e:
                logger.warning(f"  从模型加载类别名称失败: {e}")
        
        # 如果无法从模型加载，使用默认的英文类别名
        logger.warning("  使用默认类别名称")
        class_names = [
            "acer", "alocasia_macrorrhizos", "alocasia_odora", "aloe_vera", "bambusoideae",
            "cactaceae", "capsicum", "chlorophytum_comosum", "chrysanthemum_morifolium", "cicuta_virosa",
            "crassula_ovata", "cucumis_sativus", "cucurbita", "datura_stramonium", "dianthus_caryophyllus",
            "dracaena_trifasciata", "echeveria", "epipremnum_aureum", "euphorbia_pulcherrima", "ficus_lyrata",
            "gardenia_jasminoides", "gelsemium_elegans", "ginkgo_biloba", "haworthia_fasciata", "helianthus_annuus",
            "iris", "jasminum_sambac", "lilium", "malus_domestica", "monstera_deliciosa",
            "narcissus_tazetta", "nelumbo_nucifera", "nerium_oleander", "nymphaea", "orchidaceae",
            "paeonia_suffruticosa", "phragmites_australis", "pinus", "prunus_mume", "prunus_persica",
            "prunus_serrulata", "pteridophyta", "pyrus", "rosa_rugosa", "salix",
            "solanum_lycopersicum", "solanum_melongena", "spathiphyllum", "tulipa_gesneriana", "typha"
        ]
        return class_names[:self.num_classes]
    
    def detect(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        使用YOLOv10检测植物区域
        
        Args:
            image: OpenCV图像 (BGR格式)
            
        Returns:
            bbox: (x1, y1, x2, y2) 或 None
        """
        if self.detector is None:
            return None
        
        try:
            # YOLOv10推理
            results = self.detector(image, verbose=False)
            
            if len(results) > 0 and len(results[0].boxes) > 0:
                # 取置信度最高的检测框
                box = results[0].boxes[0]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                
                logger.info(f"    YOLOv10检测到植物: ({int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}), 置信度: {confidence:.2f}")
                return (int(x1), int(y1), int(x2), int(y2))
            
            return None
            
        except Exception as e:
            logger.error(f"    检测失败: {e}")
            return None
    
    def classify(self, image: np.ndarray) -> List[Dict]:
        """
        使用EfficientNet+CBAM分类
        
        Args:
            image: OpenCV图像 (RGB格式)
            
        Returns:
            分类结果列表
        """
        if self.classifier is None:
            return []
        
        try:
            # 转换为PIL Image
            pil_image = Image.fromarray(image)
            
            # 预处理
            from torchvision import transforms
            transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            img_tensor = transform(pil_image).unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                outputs = self.classifier(img_tensor)
                probabilities = F.softmax(outputs, dim=1)
            
            # 获取Top-k结果
            k = min(5, self.num_classes)
            probs, indices = torch.topk(probabilities[0], k=k)
            
            results = []
            for i, (prob, idx) in enumerate(zip(probs, indices)):
                model_class_id = idx.item()
                confidence = prob.item()
                name = self.class_names[model_class_id] if model_class_id < len(self.class_names) else f"未知{model_class_id}"
                
                # 转换为数据库的class_id
                db_class_id = get_db_class_id(model_class_id)
                
                results.append({
                    'class_id': db_class_id,  # 使用数据库的class_id
                    'model_class_id': model_class_id,  # 保留模型class_id用于调试
                    'name': name,
                    'confidence': confidence,
                    'rank': i + 1
                })
            
            return results
            
        except Exception as e:
            logger.error(f"    分类失败: {e}")
            import traceback
            traceback.print_exc()
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
            # 1. 解码图像
            nparr = np.frombuffer(image_data, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                return {'success': False, 'error': '无法解码图像', 'results': []}
            
            orig_h, orig_w = img_bgr.shape[:2]
            logger.info(f"  原始图像尺寸: {orig_w}x{orig_h}")
            
            # 2. 图像预处理
            logger.info("  [步骤1/4] 图像预处理...")
            img_processed = self.preprocessor.preprocess(img_bgr)
            logger.info(f"    预处理后尺寸: {img_processed.shape}")
            
            # 3. 检测植物区域 (使用原始图像)
            logger.info("  [步骤2/4] YOLOv10检测植物区域...")
            bbox = self.detect(img_bgr)
            
            if bbox:
                x1, y1, x2, y2 = bbox
                # 裁剪ROI
                roi_bgr = img_bgr[y1:y2, x1:x2]
                roi_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
                logger.info(f"    使用ROI区域: {roi_rgb.shape}")
            else:
                # 使用整图
                roi_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                logger.info(f"    未检测到植物区域，使用整图: {roi_rgb.shape}")
            
            # 4. 分类识别 (EfficientNet+CBAM)
            logger.info("  [步骤3/4] EfficientNet+CBAM分类...")
            results = self.classify(roi_rgb)
            
            # 5. 限制返回数量
            results = results[:top_k]
            
            logger.info(f"  [步骤4/4] 识别完成，Top {len(results)}:")
            for r in results:
                logger.info(f"    {r['rank']}. {r['name']} - {r['confidence']*100:.2f}%")
            
            return {
                'success': True,
                'bbox': bbox,
                'results': results,
                'image_size': (orig_w, orig_h),
                'method': 'Advanced (YOLOv10 + EfficientNet+CBAM)'
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
