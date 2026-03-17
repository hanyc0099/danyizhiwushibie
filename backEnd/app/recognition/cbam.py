#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CBAM (Convolutional Block Attention Module) 注意力模块
结合通道注意力(Channel Attention)和空间注意力(Spatial Attention)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ChannelAttention(nn.Module):
    """通道注意力模块"""
    
    def __init__(self, in_channels: int, reduction_ratio: int = 16):
        """
        初始化通道注意力
        
        Args:
            in_channels: 输入通道数
            reduction_ratio: 通道压缩比例
        """
        super(ChannelAttention, self).__init__()
        
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        
        # 共享MLP
        self.mlp = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // reduction_ratio, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // reduction_ratio, in_channels, 1, bias=False)
        )
        
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入特征图 [B, C, H, W]
            
        Returns:
            加权后的特征图
        """
        # 平均池化分支
        avg_out = self.mlp(self.avg_pool(x))
        # 最大池化分支
        max_out = self.mlp(self.max_pool(x))
        
        # 融合并激活
        attention = self.sigmoid(avg_out + max_out)
        
        return x * attention


class SpatialAttention(nn.Module):
    """空间注意力模块"""
    
    def __init__(self, kernel_size: int = 7):
        """
        初始化空间注意力
        
        Args:
            kernel_size: 卷积核大小
        """
        super(SpatialAttention, self).__init__()
        
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入特征图 [B, C, H, W]
            
        Returns:
            加权后的特征图
        """
        # 计算通道维度的平均和最大值
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        
        # 拼接
        concat = torch.cat([avg_out, max_out], dim=1)
        
        # 卷积生成空间注意力图
        attention = self.sigmoid(self.conv(concat))
        
        return x * attention


class CBAM(nn.Module):
    """CBAM注意力模块"""
    
    def __init__(self, in_channels: int, reduction_ratio: int = 16, spatial_kernel: int = 7):
        """
        初始化CBAM
        
        Args:
            in_channels: 输入通道数
            reduction_ratio: 通道压缩比例
            spatial_kernel: 空间注意力卷积核大小
        """
        super(CBAM, self).__init__()
        
        self.channel_attention = ChannelAttention(in_channels, reduction_ratio)
        self.spatial_attention = SpatialAttention(spatial_kernel)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入特征图 [B, C, H, W]
            
        Returns:
            注意力加权后的特征图
        """
        # 通道注意力
        x = self.channel_attention(x)
        # 空间注意力
        x = self.spatial_attention(x)
        
        return x


class EfficientNetWithCBAM(nn.Module):
    """带CBAM的EfficientNet分类器"""
    
    def __init__(self, num_classes: int = 50, pretrained: bool = True):
        """
        初始化模型
        
        Args:
            num_classes: 分类类别数
            pretrained: 是否使用预训练权重
        """
        super(EfficientNetWithCBAM, self).__init__()
        
        from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
        
        # 加载基础EfficientNet
        if pretrained:
            weights = EfficientNet_B0_Weights.IMAGENET1K_V1
        else:
            weights = None
        
        self.backbone = efficientnet_b0(weights=weights)
        
        # 获取特征维度
        in_features = self.backbone.classifier[1].in_features
        
        # 在特征提取层后添加CBAM
        # EfficientNet的特征层在features[-1]
        self.cbam = CBAM(in_channels=1280, reduction_ratio=16)  # EfficientNet-B0最后层通道数为1280
        
        # 替换分类器
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入图像 [B, 3, H, W]
            
        Returns:
            分类结果 [B, num_classes]
        """
        # 特征提取
        x = self.backbone.features(x)
        
        # CBAM注意力
        x = self.cbam(x)
        
        # 全局平均池化
        x = self.backbone.avgpool(x)
        x = torch.flatten(x, 1)
        
        # 分类
        x = self.backbone.classifier(x)
        
        return x


if __name__ == '__main__':
    # 测试CBAM模块
    print("测试CBAM模块...")
    
    # 创建测试输入
    x = torch.randn(2, 1280, 7, 7)
    
    # 测试通道注意力
    ca = ChannelAttention(1280)
    out_ca = ca(x)
    print(f"通道注意力输出形状: {out_ca.shape}")
    
    # 测试空间注意力
    sa = SpatialAttention()
    out_sa = sa(x)
    print(f"空间注意力输出形状: {out_sa.shape}")
    
    # 测试完整CBAM
    cbam = CBAM(1280)
    out_cbam = cbam(x)
    print(f"CBAM输出形状: {out_cbam.shape}")
    
    # 测试完整模型
    print("\n测试EfficientNet+CBAM模型...")
    model = EfficientNetWithCBAM(num_classes=50)
    x_img = torch.randn(2, 3, 224, 224)
    out = model(x_img)
    print(f"模型输出形状: {out.shape}")
    
    print("\n✅ 所有测试通过!")
