#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
植物识别映射层
只包含识别必需的最小信息：class_id -> english_labels 映射
"""

# 识别映射表：class_id -> 英文标签列表
# 用于 CLIP 模型零样本分类
RECOGNITION_MAP = {
    # ==================== 剧毒植物 ====================
    1: {
        "plant_id": 1,
        "labels": ["alocasia", "alocasia odora", "giant taro", "elephant ear", "chinese taro"]
    },
    2: {
        "plant_id": 2,
        "labels": ["oleander", "nerium oleander", "rose bay", "oleander flower", "nerium"]
    },
    3: {
        "plant_id": 3,
        "labels": ["datura", "datura stramonium", "jimson weed", "thorn apple", "devil's trumpet"]
    },
    4: {
        "plant_id": 4,
        "labels": ["gelsemium", "gelsemium elegans", "heartbreak grass", "false jasmine"]
    },
    5: {
        "plant_id": 5,
        "labels": ["water hemlock", "cicuta virosa", "cowbane", "poison hemlock"]
    },
    
    # ==================== 微毒植物 ====================
    6: {
        "plant_id": 6,
        "labels": ["daffodil", "narcissus", "white daffodil", "narcissus flower", "paperwhite"]
    },
    7: {
        "plant_id": 7,
        "labels": [
            "tulip", "dutch tulip", "garden tulip", "tulipa", "tulip flower",
            "red tulip", "yellow tulip", "pink tulip", "white tulip", "purple tulip",
            "orange tulip", "single tulip", "cup shaped flower", "spring flower",
            "bulb flower", "tulip bloom", "tulip petals", "colorful tulip"
        ]
    },
    8: {
        "plant_id": 8,
        "labels": ["alocasia macrorrhizos", "giant alocasia", "elephant ear plant", "taro plant"]
    },
    9: {
        "plant_id": 9,
        "labels": ["pothos", "epipremnum aureum", "devil's ivy", "golden pothos", "money plant"]
    },
    10: {
        "plant_id": 10,
        "labels": ["poinsettia", "euphorbia pulcherrima", "christmas flower", "christmas star"]
    },
    
    # ==================== 安全植物 ====================
    11: {
        "plant_id": 11,
        "labels": ["rose", "pink rose", "red rose", "white rose", "rose flower", "rosa"]
    },
    12: {
        "plant_id": 12,
        "labels": ["sunflower", "helianthus", "sun flower", "yellow sunflower"]
    },
    13: {
        "plant_id": 13,
        "labels": ["lily", "white lily", "lily flower", "lilium", "easter lily"]
    },
    14: {
        "plant_id": 14,
        "labels": ["carnation", "pink carnation", "red carnation", "dianthus", "carnation flower"]
    },
    15: {
        "plant_id": 15,
        "labels": ["chrysanthemum", "mum", "daisy", "chrysanthemum flower"]
    },
    16: {
        "plant_id": 16,
        "labels": ["orchid", "phalaenopsis", "moth orchid", "orchid flower"]
    },
    17: {
        "plant_id": 17,
        "labels": ["peony", "paeonia", "tree peony", "peony flower"]
    },
    18: {
        "plant_id": 18,
        "labels": ["lotus", "nelumbo", "lotus flower", "water lily", "sacred lotus"]
    },
    19: {
        "plant_id": 19,
        "labels": ["jasmine", "jasminum", "jasmine flower", "arabian jasmine"]
    },
    20: {
        "plant_id": 20,
        "labels": ["gardenia", "gardenia jasminoides", "cape jasmine", "gardenia flower"]
    },
    
    # 树木类植物
    21: {
        "plant_id": 21,
        "labels": ["pine", "pine tree", "pinus", "evergreen tree", "conifer"]
    },
    22: {
        "plant_id": 22,
        "labels": ["bamboo", "bamboo plant", "bambusa", "bamboo grove"]
    },
    23: {
        "plant_id": 23,
        "labels": ["maple", "maple tree", "acer", "red maple", "japanese maple"]
    },
    24: {
        "plant_id": 24,
        "labels": ["ginkgo", "ginkgo biloba", "maidenhair tree", "ginkgo tree"]
    },
    25: {
        "plant_id": 25,
        "labels": ["willow", "willow tree", "salix", "weeping willow"]
    },
    
    # 果树类
    26: {
        "plant_id": 26,
        "labels": ["apple tree", "malus", "apple blossom", "apple fruit"]
    },
    27: {
        "plant_id": 27,
        "labels": ["peach tree", "prunus persica", "peach blossom", "peach flower"]
    },
    28: {
        "plant_id": 28,
        "labels": ["pear tree", "pyrus", "pear blossom", "pear fruit"]
    },
    29: {
        "plant_id": 29,
        "labels": ["cherry tree", "prunus serrulata", "cherry blossom", "sakura"]
    },
    30: {
        "plant_id": 30,
        "labels": ["plum tree", "prunus mume", "plum blossom", "japanese apricot"]
    },
    
    # 蔬菜/草本植物
    31: {
        "plant_id": 31,
        "labels": ["tomato", "solanum lycopersicum", "tomato plant", "cherry tomato"]
    },
    32: {
        "plant_id": 32,
        "labels": ["pepper", "capsicum", "bell pepper", "chili pepper", "sweet pepper"]
    },
    33: {
        "plant_id": 33,
        "labels": ["cucumber", "cucumis sativus", "cucumber plant", "cucumber vine"]
    },
    34: {
        "plant_id": 34,
        "labels": ["eggplant", "solanum melongena", "aubergine", "eggplant plant"]
    },
    35: {
        "plant_id": 35,
        "labels": ["pumpkin", "cucurbita", "squash", "winter squash", "pumpkin vine"]
    },
    
    # 观叶植物
    36: {
        "plant_id": 36,
        "labels": ["monstera", "monstera deliciosa", "swiss cheese plant", "split leaf"]
    },
    37: {
        "plant_id": 37,
        "labels": ["fiddle leaf fig", "ficus lyrata", "ficus", "fig tree"]
    },
    38: {
        "plant_id": 38,
        "labels": ["snake plant", "sansevieria", "mother in law tongue", "dracaena"]
    },
    39: {
        "plant_id": 39,
        "labels": ["spider plant", "chlorophytum", "airplane plant", "ribbon plant"]
    },
    40: {
        "plant_id": 40,
        "labels": ["peace lily", "spathiphyllum", "spath", "white sails"]
    },
    
    # 多肉植物
    41: {
        "plant_id": 41,
        "labels": ["aloe", "aloe vera", "aloe plant", "medicinal aloe"]
    },
    42: {
        "plant_id": 42,
        "labels": ["cactus", "cacti", "succulent", "desert plant", "prickly pear"]
    },
    43: {
        "plant_id": 43,
        "labels": ["jade plant", "crassula", "crassula ovata", "money tree"]
    },
    44: {
        "plant_id": 44,
        "labels": ["echeveria", "hens and chicks", "succulent rose", "stonecrop"]
    },
    45: {
        "plant_id": 45,
        "labels": ["haworthia", "zebra plant", "succulent", "window plant"]
    },
    
    # 水生/湿地植物
    46: {
        "plant_id": 46,
        "labels": ["reed", "phragmites", "common reed", "wetland grass"]
    },
    47: {
        "plant_id": 47,
        "labels": ["cattail", "typha", "bulrush", "reed mace"]
    },
    48: {
        "plant_id": 48,
        "labels": ["water lily", "nymphaea", "pond lily", "water flower"]
    },
    49: {
        "plant_id": 49,
        "labels": ["iris", "iris flower", "bearded iris", "siberian iris"]
    },
    50: {
        "plant_id": 50,
        "labels": ["fern", "pteridophyte", "bracken", "maidenhair fern"]
    }
}


def get_all_labels():
    """获取所有英文标签列表（用于CLIP识别）"""
    all_labels = []
    label_to_class = {}
    
    for class_id, data in RECOGNITION_MAP.items():
        for label in data["labels"]:
            all_labels.append(label)
            label_to_class[label] = class_id
    
    return all_labels, label_to_class


def get_plant_id_by_class(class_id: int) -> int:
    """根据 class_id 获取 plant_id"""
    data = RECOGNITION_MAP.get(class_id)
    return data["plant_id"] if data else None


def get_class_by_plant_id(plant_id: int) -> int:
    """根据 plant_id 获取 class_id"""
    for class_id, data in RECOGNITION_MAP.items():
        if data["plant_id"] == plant_id:
            return class_id
    return None
