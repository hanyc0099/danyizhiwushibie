#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
植物数据同步脚本
将植物数据同步到数据库（使用现有表结构）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.database import Plant

# 植物数据（与数据库表结构匹配）
PLANTS_DATA = [
    # ==================== 剧毒植物 ====================
    {
        "class_id": 1,
        "chinese_name": "海芋",
        "scientific_name": "Alocasia odora",
        "family": "天南星科",
        "description": "多年生草本，叶片大，呈箭形。常生于阴湿环境、林下、溪边。分布于华南、西南地区。",
        "toxicity_level": "high",
        "toxic_parts": "块茎、汁液、叶片",
        "toxicity_symptoms": "口腔麻木、咽喉肿痛、呕吐、腹泻、严重者可致窒息",
        "emergency_advice": "立即停止食用，不要催吐，立即就医！携带植物样本"
    },
    {
        "class_id": 2,
        "chinese_name": "夹竹桃",
        "scientific_name": "Nerium oleander",
        "family": "夹竹桃科",
        "description": "常绿灌木，花色有红、白、粉等。常见于路边、公园绿化。全株有毒，燃烧烟雾亦有毒性。",
        "toxicity_level": "high",
        "toxic_parts": "全株(叶、花、茎、根、汁液)",
        "toxicity_symptoms": "恶心、呕吐、腹痛、腹泻、心律失常、严重者可致死",
        "emergency_advice": "立即就医！不要催吐！告知医生可能夹竹桃中毒"
    },
    {
        "class_id": 3,
        "chinese_name": "曼陀罗",
        "scientific_name": "Datura stramonium",
        "family": "茄科",
        "description": "一年生草本，花白色喇叭状，果实有刺。生于荒地、路旁。全株有毒，种子毒性最强。",
        "toxicity_level": "high",
        "toxic_parts": "全株(种子、花、叶、根)",
        "toxicity_symptoms": "口干、瞳孔散大、幻觉、谵妄、昏迷、呼吸抑制",
        "emergency_advice": "立即就医！保持呼吸道通畅，不要催吐"
    },
    {
        "class_id": 4,
        "chinese_name": "断肠草",
        "scientific_name": "Gelsemium elegans",
        "family": "马钱科",
        "description": "常绿藤本，花黄色。生于山地疏林中。全株剧毒，根和叶毒性最强。",
        "toxicity_level": "high",
        "toxic_parts": "全株(根、叶、花、茎)",
        "toxicity_symptoms": "眩晕、恶心、肌肉松弛、呼吸麻痹、可致死",
        "emergency_advice": "立即就医！人工呼吸，保持呼吸道通畅"
    },
    {
        "class_id": 5,
        "chinese_name": "毒芹",
        "scientific_name": "Cicuta virosa",
        "family": "伞形科",
        "description": "多年生草本，形似芹菜。生于水边、沼泽。全株剧毒，根茎毒性最强。",
        "toxicity_level": "high",
        "toxic_parts": "全株(根茎毒性最强)",
        "toxicity_symptoms": "恶心、呕吐、抽搐、呼吸麻痹、可致死",
        "emergency_advice": "立即就医！不要催吐，保持呼吸道通畅"
    },
    
    # ==================== 微毒植物 ====================
    {
        "class_id": 6,
        "chinese_name": "水仙",
        "scientific_name": "Narcissus tazetta",
        "family": "石蒜科",
        "description": "多年生草本，花白色或黄色，芳香。常见于水边、庭院。鳞茎有毒，误食可中毒。",
        "toxicity_level": "low",
        "toxic_parts": "鳞茎",
        "toxicity_symptoms": "恶心、呕吐、腹痛、腹泻",
        "emergency_advice": "多喝水，症状严重就医"
    },
    {
        "class_id": 7,
        "chinese_name": "郁金香",
        "scientific_name": "Tulipa gesneriana",
        "family": "百合科",
        "description": "多年生草本，花色丰富。常见于公园、花坛。接触汁液可能致敏。",
        "toxicity_level": "low",
        "toxic_parts": "鳞茎、汁液",
        "toxicity_symptoms": "接触皮肤可致红肿瘙痒，误食可致恶心呕吐",
        "emergency_advice": "避免接触汁液，误食后多喝水"
    },
    {
        "class_id": 8,
        "chinese_name": "滴水观音",
        "scientific_name": "Alocasia macrorrhizos",
        "family": "天南星科",
        "description": "多年生草本，叶片大。常见于室内盆栽。汁液有毒，接触皮肤可致瘙痒。",
        "toxicity_level": "low",
        "toxic_parts": "汁液、叶片",
        "toxicity_symptoms": "皮肤接触可致红肿瘙痒，误食可致口腔麻木",
        "emergency_advice": "避免接触汁液，误食后漱口就医"
    },
    {
        "class_id": 9,
        "chinese_name": "绿萝",
        "scientific_name": "Epipremnum aureum",
        "family": "天南星科",
        "description": "常绿藤本，叶片心形。常见室内盆栽。汁液有微毒，接触皮肤可致瘙痒。",
        "toxicity_level": "low",
        "toxic_parts": "汁液",
        "toxicity_symptoms": "皮肤接触可致红肿瘙痒，误食可致口腔不适",
        "emergency_advice": "避免接触汁液，误食后漱口"
    },
    {
        "class_id": 10,
        "chinese_name": "一品红",
        "scientific_name": "Euphorbia pulcherrima",
        "family": "大戟科",
        "description": "灌木，顶部叶片红色。常见于圣诞装饰。汁液有微毒。",
        "toxicity_level": "low",
        "toxic_parts": "汁液、叶片",
        "toxicity_symptoms": "皮肤接触可致红肿，误食可致恶心呕吐腹泻",
        "emergency_advice": "避免接触汁液，误食后多喝水"
    },
    
    # ==================== 安全植物 - 观赏花卉 ====================
    {
        "class_id": 11,
        "chinese_name": "玫瑰",
        "scientific_name": "Rosa rugosa",
        "family": "蔷薇科",
        "description": "落叶灌木，花色丰富，芳香。喜阳光充足，耐寒耐旱。全国各地均有栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 12,
        "chinese_name": "向日葵",
        "scientific_name": "Helianthus annuus",
        "family": "菊科",
        "description": "一年生草本，花序大，金黄色。喜阳光，耐旱。全国各地均有栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 13,
        "chinese_name": "百合",
        "scientific_name": "Lilium spp.",
        "family": "百合科",
        "description": "多年生草本，花大美丽，香气浓郁。喜凉爽湿润，耐寒。全国各地均有栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 14,
        "chinese_name": "康乃馨",
        "scientific_name": "Dianthus caryophyllus",
        "family": "石蒜科",
        "description": "多年生草本，花色丰富，花期长。喜凉爽干燥，耐寒。世界各地广泛栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 15,
        "chinese_name": "菊花",
        "scientific_name": "Chrysanthemum morifolium",
        "family": "菊科",
        "description": "多年生草本，花色丰富，花期长。喜阳光充足，耐寒。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    
    # ==================== 安全植物 - 树木 ====================
    {
        "class_id": 16,
        "chinese_name": "松树",
        "scientific_name": "Pinus",
        "family": "松科",
        "description": "常绿乔木，针叶，球果。喜阳光充足，耐寒耐旱。全国各地均有分布。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 17,
        "chinese_name": "银杏",
        "scientific_name": "Ginkgo biloba",
        "family": "银杏科",
        "description": "落叶乔木，叶片扇形，秋季变黄。喜阳光充足，耐寒。中国特产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 18,
        "chinese_name": "枫树",
        "scientific_name": "Acer",
        "family": "槭树科",
        "description": "落叶乔木，叶掌状分裂，秋季变红。喜凉爽，耐寒。北半球广泛分布。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 19,
        "chinese_name": "柳树",
        "scientific_name": "Salix",
        "family": "杨柳科",
        "description": "落叶乔木，枝条柔软下垂。喜湿润，耐寒。北半球广泛分布。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 20,
        "chinese_name": "竹子",
        "scientific_name": "Bambusoideae",
        "family": "禾本科",
        "description": "多年生草本，茎秆中空，生长迅速。喜温暖湿润。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    
    # ==================== 安全植物 - 果树 ====================
    {
        "class_id": 21,
        "chinese_name": "苹果树",
        "scientific_name": "Malus domestica",
        "family": "蔷薇科",
        "description": "落叶乔木，花粉红色，果实圆形。喜凉爽干燥，耐寒。世界各地广泛栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 22,
        "chinese_name": "桃树",
        "scientific_name": "Prunus persica",
        "family": "蔷薇科",
        "description": "落叶小乔木，花粉红色，果实多汁。喜温暖，耐寒。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 23,
        "chinese_name": "梨树",
        "scientific_name": "Pyrus",
        "family": "蔷薇科",
        "description": "落叶乔木，花白色，果实多汁。喜温暖湿润，耐寒。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 24,
        "chinese_name": "樱花树",
        "scientific_name": "Prunus serrulata",
        "family": "蔷薇科",
        "description": "落叶乔木，花粉红色或白色，花期短。喜阳光充足，耐寒。日本原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 25,
        "chinese_name": "梅花",
        "scientific_name": "Prunus mume",
        "family": "蔷薇科",
        "description": "落叶小乔木，花白色或粉红色，冬季开放。喜温暖，耐寒。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    
    # ==================== 安全植物 - 蔬菜/草本 ====================
    {
        "class_id": 26,
        "chinese_name": "番茄",
        "scientific_name": "Solanum lycopersicum",
        "family": "茄科",
        "description": "一年生草本，果实红色多汁。喜温暖，全日照。南美洲原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 27,
        "chinese_name": "辣椒",
        "scientific_name": "Capsicum",
        "family": "茄科",
        "description": "一年生草本，果实辣味。喜温暖，全日照。中南美洲原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 28,
        "chinese_name": "黄瓜",
        "scientific_name": "Cucumis sativus",
        "family": "葫芦科",
        "description": "一年生蔓生草本，果实长条形。喜温暖，全日照。印度原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 29,
        "chinese_name": "茄子",
        "scientific_name": "Solanum melongena",
        "family": "茄科",
        "description": "一年生草本，果实紫色。喜温暖，全日照。印度原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 30,
        "chinese_name": "南瓜",
        "scientific_name": "Cucurbita",
        "family": "葫芦科",
        "description": "一年生蔓生草本，果实大。喜温暖，全日照。美洲原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    
    # ==================== 安全植物 - 观叶植物 ====================
    {
        "class_id": 31,
        "chinese_name": "龟背竹",
        "scientific_name": "Monstera deliciosa",
        "family": "天南星科",
        "description": "常绿藤本，叶片大，有裂孔。喜温暖湿润，半阴。中美洲原产，室内常见。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 32,
        "chinese_name": "琴叶榕",
        "scientific_name": "Ficus lyrata",
        "family": "桑科",
        "description": "常绿乔木，叶片大，提琴形。喜温暖湿润，半阴。西非原产，室内常见。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 33,
        "chinese_name": "虎尾兰",
        "scientific_name": "Dracaena trifasciata",
        "family": "天门冬科",
        "description": "多年生草本，叶片直立，有斑纹。喜温暖干燥，耐阴。西非原产，室内常见。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 34,
        "chinese_name": "吊兰",
        "scientific_name": "Chlorophytum comosum",
        "family": "天门冬科",
        "description": "多年生草本，叶片细长，有白色条纹。喜温暖湿润，半阴。南非原产，室内常见。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 35,
        "chinese_name": "白掌",
        "scientific_name": "Spathiphyllum",
        "family": "天南星科",
        "description": "多年生草本，花白色，佛焰苞。喜温暖湿润，半阴。美洲热带原产，室内常见。",
        "toxicity_level": "safe",
    },
    
    # ==================== 安全植物 - 多肉植物 ====================
    {
        "class_id": 36,
        "chinese_name": "芦荟",
        "scientific_name": "Aloe vera",
        "family": "阿福花科",
        "description": "多年生肉质草本，叶片厚，有斑点。喜温暖干燥，全日照。阿拉伯半岛原产。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 37,
        "chinese_name": "仙人掌",
        "scientific_name": "Cactaceae",
        "family": "仙人掌科",
        "description": "多年生肉质植物，茎肥厚，有刺。喜温暖干燥，全日照。美洲原产。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 38,
        "chinese_name": "玉树",
        "scientific_name": "Crassula ovata",
        "family": "景天科",
        "description": "多年生肉质灌木，叶片厚，椭圆形。喜温暖干燥，全日照。南非原产。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 39,
        "chinese_name": "石莲花",
        "scientific_name": "Echeveria",
        "family": "景天科",
        "description": "多年生肉质草本，叶片莲座状排列。喜温暖干燥，全日照。美洲原产。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 40,
        "chinese_name": "条纹十二卷",
        "scientific_name": "Haworthia fasciata",
        "family": "阿福花科",
        "description": "多年生肉质草本，叶片厚，有白色条纹。喜温暖干燥，半阴。南非原产。",
        "toxicity_level": "safe",
    },
    
    # ==================== 安全植物 - 水生/湿地 ====================
    {
        "class_id": 41,
        "chinese_name": "芦苇",
        "scientific_name": "Phragmites australis",
        "family": "禾本科",
        "description": "多年生草本，茎秆高大，生长在水边。喜湿润，耐寒。世界各地广泛分布。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 42,
        "chinese_name": "香蒲",
        "scientific_name": "Typha",
        "family": "香蒲科",
        "description": "多年生草本，花序圆柱形，生长在水边。喜湿润，耐寒。世界各地广泛分布。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 43,
        "chinese_name": "睡莲",
        "scientific_name": "Nymphaea",
        "family": "睡莲科",
        "description": "多年生水生草本，花美丽，浮于水面。喜温暖，全日照。世界各地广泛分布。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 44,
        "chinese_name": "荷花",
        "scientific_name": "Nelumbo nucifera",
        "family": "莲科",
        "description": "多年生水生草本，花大美丽。喜温暖，全日照。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 45,
        "chinese_name": "鸢尾",
        "scientific_name": "Iris",
        "family": "鸢尾科",
        "description": "多年生草本，花美丽，颜色丰富。喜湿润，耐寒。北半球广泛分布。",
        "toxicity_level": "safe",
    },
    
    # ==================== 安全植物 - 其他 ====================
    {
        "class_id": 46,
        "chinese_name": "兰花",
        "scientific_name": "Orchidaceae",
        "family": "兰科",
        "description": "多年生草本，花形优美，色彩丰富。喜温暖湿润，半阴。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 47,
        "chinese_name": "牡丹",
        "scientific_name": "Paeonia suffruticosa",
        "family": "芍药科",
        "description": "落叶灌木，花大美丽，被誉为'花中之王'。喜凉爽干燥，耐寒。中国原产。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 48,
        "chinese_name": "茉莉花",
        "scientific_name": "Jasminum sambac",
        "family": "木犀科",
        "description": "常绿灌木，花白色芳香。喜温暖湿润，半阴。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 49,
        "chinese_name": "栀子花",
        "scientific_name": "Gardenia jasminoides",
        "family": "茜草科",
        "description": "常绿灌木，花白色芳香。喜温暖湿润，半阴。中国原产，世界各地栽培。",
        "toxicity_level": "safe",
    },
    {
        "class_id": 50,
        "chinese_name": "蕨类",
        "scientific_name": "Pteridophyta",
        "family": "蕨类植物",
        "description": "多年生草本，叶片羽状分裂，喜阴湿。世界各地广泛分布。",
        "toxicity_level": "safe",
    }
]


def sync_plants():
    """同步植物数据到数据库"""
    db = SessionLocal()
    try:
        print("开始同步植物数据到数据库...")
        
        added_count = 0
        updated_count = 0
        
        for plant_data in PLANTS_DATA:
            # 检查是否已存在
            existing = db.query(Plant).filter(Plant.class_id == plant_data["class_id"]).first()
            
            if existing:
                # 更新现有记录
                for key, value in plant_data.items():
                    setattr(existing, key, value)
                updated_count += 1
                print(f"  更新: {plant_data['chinese_name']}")
            else:
                # 创建新记录
                plant = Plant(**plant_data)
                db.add(plant)
                added_count += 1
                print(f"  新增: {plant_data['chinese_name']}")
        
        db.commit()
        print(f"\n同步完成！")
        print(f"  新增: {added_count} 种")
        print(f"  更新: {updated_count} 种")
        print(f"  总计: {added_count + updated_count} 种")
        
    except Exception as e:
        db.rollback()
        print(f"同步失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # 同步数据
    sync_plants()
