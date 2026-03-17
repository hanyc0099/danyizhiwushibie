#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
类别名称映射
将模型输出的英文类别名映射到数据库的class_id
"""

# 模型类别索引 -> 数据库class_id 的映射
# 基于模型训练时的字母顺序和数据库的实际顺序
MODEL_TO_DB_MAPPING = {
    0: 22,   # acer -> ginkgo_biloba (银杏)
    1: 30,   # alocasia_macrorrhizos -> nelumbo_nucifera (荷花)
    2: 31,   # alocasia_odora -> nerium_oleander (夹竹桃)
    3: 35,   # aloe_vera -> aloe_vera (芦荟)
    4: 37,   # bambusoideae -> echeveria (多肉)
    5: 36,   # cactaceae -> cactaceae (仙人掌)
    6: 45,   # capsicum -> solanum_lycopersicum (番茄)
    7: 1,    # chlorophytum_comosum -> chlorophytum_comosum (吊兰)
    8: 34,   # chrysanthemum_morifolium -> chrysanthemum_morifolium (菊花)
    9: 32,   # cicuta_virosa -> nymphaea (睡莲)
    10: 38,  # crassula_ovata -> lithops (生石花)
    11: 46,  # cucumis_sativus -> solanum_melongena (茄子)
    12: 47,  # cucurbita -> spathiphyllum (白掌)
    13: 33,  # datura_stramonium -> bougainvillea_glabra (三角梅)
    14: 26,  # dianthus_caryophyllus -> dianthus_caryophyllus (康乃馨)
    15: 2,   # dracaena_trifasciata -> dracaena_trifasciata (虎尾兰)
    16: 37,  # echeveria -> echeveria (多肉)
    17: 0,   # epipremnum_aureum -> epipremnum_aureum (绿萝)
    18: 39,  # euphorbia_pulcherrima -> haworthia_fasciata (玉露)
    19: 6,   # ficus_lyrata -> ficus_lyrata (琴叶榕)
    20: 17,  # gardenia_jasminoides -> gardenia_jasminoides (栀子花)
    21: 40,  # gelsemium_elegans -> cotyledon_tomentosa (熊童子)
    22: 22,  # ginkgo_biloba -> ginkgo_biloba (银杏)
    23: 39,  # haworthia_fasciata -> haworthia_fasciata (玉露)
    24: 41,  # helianthus_annuus -> echeveria_chihuahuaensis (吉娃娃)
    25: 25,  # iris -> hydrangea_macrophylla (绣球花)
    26: 16,  # jasminum_sambac -> jasminum_sambac (茉莉花)
    27: 27,  # lilium -> lilium (百合)
    28: 42,  # malus_domestica -> sedum_rubrotinctum (虹之玉)
    29: 3,   # monstera_deliciosa -> monstera_deliciosa (龟背竹)
    30: 30,  # narcissus_tazetta -> narcissus_tazetta (水仙)
    31: 30,  # nelumbo_nucifera -> nelumbo_nucifera (荷花)
    32: 31,  # nerium_oleander -> nerium_oleander (夹竹桃)
    33: 32,  # nymphaea -> nymphaea (睡莲)
    34: 19,  # orchidaceae -> phalaenopsis_aprodite (蝴蝶兰)
    35: 25,  # paeonia_suffruticosa -> paeonia_suffruticosa (牡丹)
    36: 48,  # phragmites_australis -> adiantum (铁线蕨)
    37: 38,  # pinus -> lithops (生石花)
    38: 38,  # prunus_mume -> lithops (生石花)
    39: 40,  # prunus_persica -> cotyledon_tomentosa (熊童子)
    40: 41,  # prunus_serrulata -> echeveria_chihuahuaensis (吉娃娃)
    41: 48,  # pteridophyta -> adiantum (铁线蕨)
    42: 42,  # pyrus -> sedum_rubrotinctum (虹之玉)
    43: 15,  # rosa_rugosa -> rosa_chinensis (月季)
    44: 44,  # salix -> aeonium_arboreum (法师)
    45: 45,  # solanum_lycopersicum -> solanum_lycopersicum (番茄)
    46: 46,  # solanum_melongena -> solanum_melongena (茄子)
    47: 32,  # spathiphyllum -> spathiphyllum (白掌)
    48: 28,  # tulipa_gesneriana -> tulipa_gesneriana (郁金香)
    49: 49,  # typha -> tillandsia (空气凤梨)
}

# 反向映射：数据库class_id -> 模型类别索引
DB_TO_MODEL_MAPPING = {v: k for k, v in MODEL_TO_DB_MAPPING.items()}


def get_db_class_id(model_class_id: int) -> int:
    """
    将模型输出的类别索引转换为数据库的class_id
    
    Args:
        model_class_id: 模型输出的类别索引
        
    Returns:
        数据库的class_id
    """
    return MODEL_TO_DB_MAPPING.get(model_class_id, model_class_id)


def get_model_class_id(db_class_id: int) -> int:
    """
    将数据库的class_id转换为模型类别索引
    
    Args:
        db_class_id: 数据库的class_id
        
    Returns:
        模型类别索引
    """
    return DB_TO_MODEL_MAPPING.get(db_class_id, db_class_id)
