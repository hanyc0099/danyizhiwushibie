#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成模型索引到数据库 class_id 的映射
"""
import os
import sys
import json

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.database import Plant

db = SessionLocal()

# 从 Android assets 读取模型类别名称
android_assets_path = os.path.join(os.path.dirname(backend_dir), 'android', 'app', 'src', 'main', 'assets')
with open(os.path.join(android_assets_path, 'plant_50class.json'), 'r', encoding='utf-8') as f:
    model_classes = json.load(f)['classes']

# 从数据库读取植物信息
plants = db.query(Plant).all()
plant_map = {p.chinese_name: p.class_id for p in plants}

print("=== 模型索引到数据库 class_id 映射 ===\n")

mapping = []
for i, name in enumerate(model_classes):
    db_class_id = plant_map.get(name)
    if db_class_id is not None:
        mapping.append({
            "model_index": i,
            "db_class_id": db_class_id,
            "name": name
        })
        print(f"模型索引 {i:2d} -> 数据库 class_id {db_class_id:2d}: {name}")
    else:
        print(f"模型索引 {i:2d} -> 未找到: {name}")

# 保存映射文件
output_path = os.path.join(android_assets_path, 'class_mapping.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

print(f"\n映射文件已保存到: {output_path}")

db.close()
