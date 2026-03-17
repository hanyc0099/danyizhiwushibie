#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接管理
"""

import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

# 全局引擎和会话工厂
_engine = None
_SessionLocal = None


def init_db(db_path: str = None):
    """
    初始化数据库
    
    Args:
        db_path: 数据库文件路径，默认使用项目目录下的 plant_recognition.db
    """
    global _engine, _SessionLocal
    
    if db_path is None:
        # 默认数据库路径
        base_path = Path(__file__).parent.parent.parent
        db_path = base_path / "database" / "plant_recognition.db"
        db_path.parent.mkdir(exist_ok=True)
        db_path = str(db_path)
    
    logger.info(f"[数据库] 初始化: {db_path}")
    
    # 创建引擎
    _engine = create_engine(
        f'sqlite:///{db_path}',
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # 创建会话工厂
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    # 创建表结构
    from app.models.database import Base
    Base.metadata.create_all(bind=_engine)
    
    logger.info("[数据库] 初始化完成")
    
    # 检查是否需要初始化数据
    _check_and_init_data()
    
    return _engine


def _check_and_init_data():
    """检查并初始化基础数据"""
    db = _SessionLocal()
    try:
        from app.models.database import Plant
        
        # 检查是否有数据
        count = db.query(Plant).count()
        if count == 0:
            logger.info("[数据库] 初始化植物数据...")
            _init_plants_data(db)
        else:
            logger.info(f"[数据库] 已有 {count} 条植物数据")
    finally:
        db.close()


def _init_plants_data(db: Session):
    """初始化植物数据"""
    from app.models.database import Plant
    
    # 50种观赏植物数据
    plants_data = [
        # 室内观叶植物 (0-14)
        {"class_id": 0, "chinese_name": "绿萝", "english_name": "Pothos", "scientific_name": "Epipremnum aureum", "family": "天南星科", "genus": "麒麟叶属", "description": "绿萝是常见的室内观叶植物，叶片心形、翠绿，具有极强的生命力和空气净化能力。", "characteristics": "藤本植物，叶片心形革质，叶色翠绿或带有金黄色斑纹。", "flowering_period": "很少开花", "care_tips": "喜散射光，忌强光直射；保持土壤微湿，忌积水；适宜温度15-25℃。", "difficulty_level": 1},
        {"class_id": 1, "chinese_name": "吊兰", "english_name": "Spider Plant", "scientific_name": "Chlorophytum comosum", "family": "百合科", "genus": "吊兰属", "description": "吊兰叶片细长柔软，四季常青，是优良的室内净化植物。", "characteristics": "叶片基生呈莲座状，细长带状，叶缘绿色或镶有白色或黄色条纹。", "flowering_period": "春夏开花", "care_tips": "喜半阴环境；保持土壤湿润；适宜温度15-25℃。", "difficulty_level": 1},
        {"class_id": 2, "chinese_name": "虎尾兰", "english_name": "Snake Plant", "scientific_name": "Sansevieria trifasciata", "family": "百合科", "genus": "虎尾兰属", "description": "虎尾兰叶片坚挺直立，有灰白和深绿相间的虎尾状斑纹。", "characteristics": "叶片直立丛生，剑形革质，表面有灰白和深绿相间的横纹。", "flowering_period": "夏秋开花", "care_tips": "极耐旱，宁干勿湿；喜光也耐阴；适宜温度18-27℃。", "difficulty_level": 1},
        {"class_id": 3, "chinese_name": "龟背竹", "english_name": "Monstera", "scientific_name": "Monstera deliciosa", "family": "天南星科", "genus": "龟背竹属", "description": "龟背竹叶形奇特，孔裂纹状，极具热带风情。", "characteristics": "叶片大呈心形，成熟叶羽状分裂具孔洞。", "flowering_period": "夏秋开花", "care_tips": "喜半阴，忌强光；保持土壤湿润；适宜温度20-30℃。", "difficulty_level": 2},
        {"class_id": 4, "chinese_name": "发财树", "english_name": "Money Tree", "scientific_name": "Pachira aquatica", "family": "锦葵科", "genus": "瓜栗属", "description": "发财树茎干基部膨大，枝叶茂密，寓意吉祥。", "characteristics": "茎基部膨大如瓶，掌状复叶，小叶5-9片。", "flowering_period": "5-11月开花", "care_tips": "喜散射光；宁干勿湿，忌积水；适宜温度18-30℃。", "difficulty_level": 1},
        {"class_id": 5, "chinese_name": "橡皮树", "english_name": "Rubber Plant", "scientific_name": "Ficus elastica", "family": "桑科", "genus": "榕属", "description": "橡皮树叶片肥厚宽大，革质有光泽，是著名的室内观叶植物。", "characteristics": "叶片大呈椭圆形，革质厚而有光泽。", "flowering_period": "很少开花", "care_tips": "喜充足光照；保持土壤湿润；适宜温度20-30℃。", "difficulty_level": 2},
        {"class_id": 6, "chinese_name": "琴叶榕", "english_name": "Fiddle Leaf Fig", "scientific_name": "Ficus lyrata", "family": "桑科", "genus": "榕属", "description": "琴叶榕叶片大提琴形，叶脉清晰，株型优美。", "characteristics": "叶片提琴形，革质，叶脉明显。", "flowering_period": "很少开花", "care_tips": "喜充足散射光；适宜温度20-35℃；注意通风。", "difficulty_level": 3},
        {"class_id": 7, "chinese_name": "富贵竹", "english_name": "Lucky Bamboo", "scientific_name": "Dracaena sanderiana", "family": "天门冬科", "genus": "龙血树属", "description": "富贵竹茎节分明，常水培，寓意吉祥。", "characteristics": "茎直立有节，叶片线形披针状。", "flowering_period": "很少开花", "care_tips": "水培保持水质清洁；散射光即可；适宜温度18-24℃。", "difficulty_level": 1},
        {"class_id": 8, "chinese_name": "文竹", "english_name": "Asparagus Fern", "scientific_name": "Asparagus setaceus", "family": "天门冬科", "genus": "天门冬属", "description": "文竹枝叶细密如羽毛，姿态优雅。", "characteristics": "茎细软，叶状枝纤细如羽毛，密生呈云片状。", "flowering_period": "夏秋开花", "care_tips": "喜半阴，忌强光；保持土壤湿润；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 9, "chinese_name": "铜钱草", "english_name": "Pennywort", "scientific_name": "Hydrocotyle vulgaris", "family": "伞形科", "genus": "天胡荽属", "description": "铜钱草叶片圆润如铜钱，生命力强。", "characteristics": "叶片圆形或肾形，匍匐茎繁殖力强。", "flowering_period": "夏秋开花", "care_tips": "喜充足光照；喜水湿环境；适宜温度15-25℃。", "difficulty_level": 1},
        {"class_id": 10, "chinese_name": "豆瓣绿", "english_name": "Peperomia", "scientific_name": "Peperomia tetraphylla", "family": "胡椒科", "genus": "草胡椒属", "description": "豆瓣绿叶片肥厚翠绿，小巧玲珑。", "characteristics": "叶片对生或轮生，肉质肥厚，卵形或椭圆形。", "flowering_period": "春末夏初开花", "care_tips": "喜半阴环境；宁干勿湿；适宜温度20-30℃。", "difficulty_level": 1},
        {"class_id": 11, "chinese_name": "常春藤", "english_name": "Ivy", "scientific_name": "Hedera helix", "family": "五加科", "genus": "常春藤属", "description": "常春藤四季常青，叶形优美，是优良的垂直绿化植物。", "characteristics": "叶片革质，三角状卵形或掌状裂。", "flowering_period": "秋季开花", "care_tips": "喜半阴环境；保持土壤湿润；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 12, "chinese_name": "绿萝藤", "english_name": "Philodendron", "scientific_name": "Philodendron hederaceum", "family": "天南星科", "genus": "喜林芋属", "description": "绿萝藤心形叶片翠绿，攀援性强。", "characteristics": "叶片心形，质地薄，叶色翠绿。", "flowering_period": "很少开花", "care_tips": "喜散射光；保持土壤湿润；适宜温度18-25℃。", "difficulty_level": 1},
        {"class_id": 13, "chinese_name": "一叶兰", "english_name": "Cast Iron Plant", "scientific_name": "Aspidistra elatior", "family": "天门冬科", "genus": "蜘蛛抱蛋属", "description": "一叶兰叶片挺拔，极耐阴，是优良的室内阴生植物。", "characteristics": "叶片单生，长椭圆形或披针形，革质。", "flowering_period": "春夏季开花", "care_tips": "极耐阴，忌强光；耐旱怕涝；适宜温度10-25℃。", "difficulty_level": 1},
        {"class_id": 14, "chinese_name": "万年青", "english_name": "Chinese Evergreen", "scientific_name": "Aglaonema modestum", "family": "天南星科", "genus": "粗肋草属", "description": "万年青叶片浓绿，有银白色斑纹，寓意吉祥。", "characteristics": "叶片长椭圆形，叶面有银白色或粉红色斑纹。", "flowering_period": "夏秋季开花", "care_tips": "喜半阴环境；保持土壤湿润；适宜温度18-30℃。", "difficulty_level": 1},
        
        # 开花观赏植物 (15-34)
        {"class_id": 15, "chinese_name": "月季", "english_name": "Rose", "scientific_name": "Rosa chinensis", "family": "蔷薇科", "genus": "蔷薇属", "description": "月季花型优美，花色丰富，被称为花中皇后。", "characteristics": "茎有刺，奇数羽状复叶，花单生或簇生。", "flowering_period": "4-11月多次开花", "care_tips": "喜充足阳光；定期修剪促花；注意病虫害防治。", "difficulty_level": 2},
        {"class_id": 16, "chinese_name": "茉莉花", "english_name": "Jasmine", "scientific_name": "Jasminum sambac", "family": "木犀科", "genus": "素馨属", "description": "茉莉花洁白芳香，是著名的香花植物。", "characteristics": "叶片对生，花白色，重瓣或单瓣，香气浓郁。", "flowering_period": "5-10月开花", "care_tips": "喜充足阳光；喜湿润怕积水；适宜温度25-35℃。", "difficulty_level": 2},
        {"class_id": 17, "chinese_name": "栀子花", "english_name": "Gardenia", "scientific_name": "Gardenia jasminoides", "family": "茜草科", "genus": "栀子属", "description": "栀子花洁白如玉，芳香四溢，是夏季重要的香花植物。", "characteristics": "叶片对生，革质有光泽，花白色高脚碟状。", "flowering_period": "5-8月开花", "care_tips": "喜半阴环境；喜酸性土壤；适宜温度18-28℃。", "difficulty_level": 2},
        {"class_id": 18, "chinese_name": "杜鹃花", "english_name": "Azalea", "scientific_name": "Rhododendron simsii", "family": "杜鹃花科", "genus": "杜鹃属", "description": "杜鹃花色彩艳丽，被誉为花中西施。", "characteristics": "叶片互生，花顶生，花冠漏斗状。", "flowering_period": "4-6月开花", "care_tips": "喜半阴环境；喜酸性土壤；适宜温度12-25℃。", "difficulty_level": 3},
        {"class_id": 19, "chinese_name": "蝴蝶兰", "english_name": "Moth Orchid", "scientific_name": "Phalaenopsis aphrodite", "family": "兰科", "genus": "蝴蝶兰属", "description": "蝴蝶兰花姿如蝶，花色高雅，花期长。", "characteristics": "叶片肉质，花茎直立，花朵如蝴蝶。", "flowering_period": "冬春开花", "care_tips": "喜散射光，忌强光；忌积水；适宜温度18-28℃。", "difficulty_level": 3},
        {"class_id": 20, "chinese_name": "君子兰", "english_name": "Clivia", "scientific_name": "Clivia miniata", "family": "石蒜科", "genus": "君子兰属", "description": "君子兰叶片宽厚整齐，花茎挺拔，花朵鲜艳。", "characteristics": "叶片宽带状，肉质革质，花茎直立，伞形花序。", "flowering_period": "冬春开花", "care_tips": "喜半阴环境；耐旱怕涝；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 21, "chinese_name": "长寿花", "english_name": "Kalanchoe", "scientific_name": "Kalanchoe blossfeldiana", "family": "景天科", "genus": "伽蓝菜属", "description": "长寿花花期长，花色丰富，寓意健康长寿。", "characteristics": "叶片对生，肉质，花簇生。", "flowering_period": "12-次年5月开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度15-25℃。", "difficulty_level": 1},
        {"class_id": 22, "chinese_name": "蟹爪兰", "english_name": "Christmas Cactus", "scientific_name": "Schlumbergera truncata", "family": "仙人掌科", "genus": "蟹爪兰属", "description": "蟹爪兰茎节如蟹爪，花朵艳丽，花期正值圣诞节前后。", "characteristics": "茎节扁平呈蟹爪状，花单生茎节顶端。", "flowering_period": "11-次年2月开花", "care_tips": "喜半阴环境；生长期保持湿润；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 23, "chinese_name": "仙客来", "english_name": "Cyclamen", "scientific_name": "Cyclamen persicum", "family": "报春花科", "genus": "仙客来属", "description": "仙客来花朵独特，花瓣反卷，花叶并茂。", "characteristics": "块茎扁球形，叶心形，花单生，花瓣反卷。", "flowering_period": "11-次年4月开花", "care_tips": "喜凉爽环境；忌积水；适宜温度10-20℃。", "difficulty_level": 3},
        {"class_id": 24, "chinese_name": "天竺葵", "english_name": "Geranium", "scientific_name": "Pelargonium hortorum", "family": "牻牛儿苗科", "genus": "天竺葵属", "description": "天竺葵花色丰富，花期长，有特殊香气。", "characteristics": "茎肉质，叶片掌状浅裂，伞形花序。", "flowering_period": "春夏秋开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度15-25℃。", "difficulty_level": 1},
        {"class_id": 25, "chinese_name": "绣球花", "english_name": "Hydrangea", "scientific_name": "Hydrangea macrophylla", "family": "虎耳草科", "genus": "绣球属", "description": "绣球花花球硕大，花色可变，从蓝到粉红。", "characteristics": "叶片对生，花大型球状聚伞花序。", "flowering_period": "6-8月开花", "care_tips": "喜半阴环境；保持土壤湿润；喜酸性土壤。", "difficulty_level": 2},
        {"class_id": 26, "chinese_name": "康乃馨", "english_name": "Carnation", "scientific_name": "Dianthus caryophyllus", "family": "石竹科", "genus": "石竹属", "description": "康乃馨花朵端庄，花香清幽，是母亲节的象征花卉。", "characteristics": "茎直立，叶片线状披针形，花瓣有锯齿。", "flowering_period": "4-9月开花", "care_tips": "喜充足阳光；排水良好；适宜温度14-21℃。", "difficulty_level": 2},
        {"class_id": 27, "chinese_name": "百合", "english_name": "Lily", "scientific_name": "Lilium brownii", "family": "百合科", "genus": "百合属", "description": "百合花姿优雅，花香浓郁，寓意纯洁高雅。", "characteristics": "茎直立，叶片披针形，花大喇叭状。", "flowering_period": "6-8月开花", "care_tips": "喜充足阳光；保持土壤湿润；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 28, "chinese_name": "郁金香", "english_name": "Tulip", "scientific_name": "Tulipa gesneriana", "family": "百合科", "genus": "郁金香属", "description": "郁金香花型优美，色彩绚丽，是荷兰国花。", "characteristics": "鳞茎卵形，叶片带状披针形，杯状花。", "flowering_period": "3-5月开花", "care_tips": "喜充足阳光；排水良好；适宜温度8-20℃。", "difficulty_level": 2},
        {"class_id": 29, "chinese_name": "风信子", "english_name": "Hyacinth", "scientific_name": "Hyacinthus orientalis", "family": "天门冬科", "genus": "风信子属", "description": "风信子花序紧密，花香浓郁，是春季重要的球根花卉。", "characteristics": "鳞茎卵形，总状花序密生，花色丰富芳香。", "flowering_period": "3-4月开花", "care_tips": "喜充足阳光；保持土壤湿润；适宜温度15-25℃。", "difficulty_level": 1},
        {"class_id": 30, "chinese_name": "水仙", "english_name": "Narcissus", "scientific_name": "Narcissus tazetta", "family": "石蒜科", "genus": "水仙属", "description": "水仙花清香雅致，是中国传统名花，春节前后开花。", "characteristics": "鳞茎卵球形，叶片带状，花白色副冠黄色。", "flowering_period": "10-次年2月开花", "care_tips": "喜充足阳光；水培或土培；适宜温度10-20℃。", "difficulty_level": 1},
        {"class_id": 31, "chinese_name": "红掌", "english_name": "Anthurium", "scientific_name": "Anthurium andraeanum", "family": "天南星科", "genus": "花烛属", "description": "红掌佛焰苞鲜红，花期长，是高档的室内观赏花卉。", "characteristics": "叶片心形革质，佛焰苞鲜红，肉穗花序黄色。", "flowering_period": "全年开花", "care_tips": "喜半阴环境；喜高温高湿；适宜温度20-30℃。", "difficulty_level": 2},
        {"class_id": 32, "chinese_name": "白掌", "english_name": "Peace Lily", "scientific_name": "Spathiphyllum kochii", "family": "天南星科", "genus": "苞叶芋属", "description": "白掌佛焰苞白色，清新雅致，有一帆风顺的美好寓意。", "characteristics": "叶片长椭圆形，佛焰苞白色。", "flowering_period": "春夏开花", "care_tips": "喜半阴环境；保持土壤湿润；适宜温度18-25℃。", "difficulty_level": 1},
        {"class_id": 33, "chinese_name": "三角梅", "english_name": "Bougainvillea", "scientific_name": "Bougainvillea spectabilis", "family": "紫茉莉科", "genus": "叶子花属", "description": "三角梅花苞片艳丽，花期长，是热带重要的观赏植物。", "characteristics": "叶片卵形，花小，花苞片三枚，颜色鲜艳。", "flowering_period": "冬春开花", "care_tips": "喜充足阳光；耐旱怕涝；适宜温度15-30℃。", "difficulty_level": 2},
        {"class_id": 34, "chinese_name": "菊花", "english_name": "Chrysanthemum", "scientific_name": "Chrysanthemum morifolium", "family": "菊科", "genus": "菊属", "description": "菊花是中国传统名花，花型丰富，色彩多样。", "characteristics": "茎直立，叶片卵形，头状花序，花色丰富。", "flowering_period": "9-11月开花", "care_tips": "喜充足阳光；保持土壤湿润；适宜温度15-25℃。", "difficulty_level": 2},
        
        # 多肉植物 (35-44)
        {"class_id": 35, "chinese_name": "芦荟", "english_name": "Aloe", "scientific_name": "Aloe vera", "family": "百合科", "genus": "芦荟属", "description": "芦荟叶片肥厚多汁，具有美容和药用价值。", "characteristics": "叶片莲座状排列，肉质肥厚，叶缘有刺。", "flowering_period": "冬春开花", "care_tips": "喜充足阳光；极耐旱，宁干勿湿；适宜温度15-35℃。", "difficulty_level": 1},
        {"class_id": 36, "chinese_name": "仙人掌", "english_name": "Cactus", "scientific_name": "Opuntia dillenii", "family": "仙人掌科", "genus": "仙人掌属", "description": "仙人掌形态奇特，生命力强，是典型的沙漠植物。", "characteristics": "茎肉质扁平或柱状，刺座上有刺。", "flowering_period": "6-8月开花", "care_tips": "喜充足阳光；极耐旱，忌积水；适宜温度20-35℃。", "difficulty_level": 1},
        {"class_id": 37, "chinese_name": "多肉组合", "english_name": "Succulent", "scientific_name": "Echeveria spp.", "family": "景天科", "genus": "石莲花属", "description": "多肉植物叶片肥厚，形态可爱，色彩丰富。", "characteristics": "叶片莲座状排列，肉质，叶色绿、粉、红、紫等。", "flowering_period": "春秋季开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度15-25℃。", "difficulty_level": 1},
        {"class_id": 38, "chinese_name": "生石花", "english_name": "Living Stone", "scientific_name": "Lithops pseudotruncatella", "family": "番杏科", "genus": "生石花属", "description": "生石花外形如卵石，是典型的拟态植物。", "characteristics": "植株由一对肉质叶片组成，顶部有窗。", "flowering_period": "秋季开花", "care_tips": "喜充足阳光；极少浇水，夏冬季休眠断水；适宜温度15-25℃。", "difficulty_level": 3},
        {"class_id": 39, "chinese_name": "玉露", "english_name": "Haworthia", "scientific_name": "Haworthia cooperi", "family": "百合科", "genus": "十二卷属", "description": "玉露叶片晶莹剔透，顶部透明如窗，是多肉中的精品。", "characteristics": "叶片莲座状排列，肉质透明，顶端透明如窗。", "flowering_period": "春夏季开花", "care_tips": "喜散射光，忌强光；适宜温度15-25℃；需较高湿度。", "difficulty_level": 2},
        {"class_id": 40, "chinese_name": "熊童子", "english_name": "Bear Paw", "scientific_name": "Cotyledon tomentosa", "family": "景天科", "genus": "银波锦属", "description": "熊童子叶片如小熊爪子，顶端有红指甲，可爱萌趣。", "characteristics": "叶片对生，肉质肥厚，密生白色绒毛，顶端红色。", "flowering_period": "夏季开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 41, "chinese_name": "吉娃娃", "english_name": "Chihuahua", "scientific_name": "Echeveria chihuahuaensis", "family": "景天科", "genus": "石莲花属", "description": "吉娃娃叶片紧凑，叶尖红艳，是多肉植物中的经典品种。", "characteristics": "叶片莲座状排列，叶尖红色，叶面有白粉。", "flowering_period": "春季开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度10-25℃。", "difficulty_level": 1},
        {"class_id": 42, "chinese_name": "虹之玉", "english_name": "Jelly Bean", "scientific_name": "Sedum rubrotinctum", "family": "景天科", "genus": "景天属", "description": "虹之玉叶片圆润如豆子，日照充足时变红。", "characteristics": "叶片圆柱形，肉质，绿色或红色，易群生。", "flowering_period": "春季开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度10-28℃。", "difficulty_level": 1},
        {"class_id": 43, "chinese_name": "法师", "english_name": "Aeonium", "scientific_name": "Aeonium arboreum", "family": "景天科", "genus": "莲花掌属", "description": "法师株型如莲花，叶片层层叠叠，颜色从绿到黑紫。", "characteristics": "叶片莲座状排列于枝顶，叶色绿、紫、黑等。", "flowering_period": "春季开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 44, "chinese_name": "锦晃星", "english_name": "Red Velvet", "scientific_name": "Echeveria pulvinata", "family": "景天科", "genus": "石莲花属", "description": "锦晃星叶片和茎干密生绒毛，叶缘红色，触感柔软。", "characteristics": "叶片莲座状，密生绒毛，叶缘红色。", "flowering_period": "冬季开花", "care_tips": "喜充足阳光；宁干勿湿；适宜温度10-25℃。", "difficulty_level": 2},
        
        # 水培/香草植物 (45-49)
        {"class_id": 45, "chinese_name": "薄荷", "english_name": "Mint", "scientific_name": "Mentha haplocalyx", "family": "唇形科", "genus": "薄荷属", "description": "薄荷叶片芳香，可食用可泡茶，是常见的香草植物。", "characteristics": "茎四棱，叶片对生，卵形，揉搓有清凉香气。", "flowering_period": "7-9月开花", "care_tips": "喜充足阳光或半阴；保持土壤湿润；适宜温度20-30℃。", "difficulty_level": 1},
        {"class_id": 46, "chinese_name": "迷迭香", "english_name": "Rosemary", "scientific_name": "Rosmarinus officinalis", "family": "唇形科", "genus": "迷迭香属", "description": "迷迭香叶片芳香，是西餐常用香料，也是优良的观赏植物。", "characteristics": "叶片线形革质，背面有白毛，花蓝紫色。", "flowering_period": "春夏开花", "care_tips": "喜充足阳光；耐旱怕涝；适宜温度15-30℃。", "difficulty_level": 2},
        {"class_id": 47, "chinese_name": "薰衣草", "english_name": "Lavender", "scientific_name": "Lavandula angustifolia", "family": "唇形科", "genus": "薰衣草属", "description": "薰衣草花穗蓝紫，芳香浓郁，是著名的香料和观赏植物。", "characteristics": "叶片线形灰绿，花穗状蓝紫色，芳香。", "flowering_period": "6-8月开花", "care_tips": "喜充足阳光；耐旱怕涝；适宜温度15-25℃。", "difficulty_level": 2},
        {"class_id": 48, "chinese_name": "铁线蕨", "english_name": "Maidenhair Fern", "scientific_name": "Adiantum capillus-veneris", "family": "铁线蕨科", "genus": "铁线蕨属", "description": "铁线蕨叶片优美，叶柄黑色如铁丝，是优良的室内阴生蕨类。", "characteristics": "叶柄细圆黑色，叶片扇状分裂，叶脉羽状。", "flowering_period": "四季常绿", "care_tips": "喜阴湿环境；忌强光；适宜温度13-22℃。", "difficulty_level": 2},
        {"class_id": 49, "chinese_name": "空气凤梨", "english_name": "Air Plant", "scientific_name": "Tillandsia ionantha", "family": "凤梨科", "genus": "空气凤梨属", "description": "空气凤梨无需土壤，靠叶片吸收水分和养分，是极具特色的现代观赏植物。", "characteristics": "无根或根系退化，叶片银灰色鳞片状，靠叶面吸收水分。", "flowering_period": "秋冬季开花", "care_tips": "散射光即可；每周喷水2-3次；适宜温度15-30℃。", "difficulty_level": 1},
    ]
    
    # 插入数据
    for plant_data in plants_data:
        plant = Plant(**plant_data)
        db.add(plant)
    
    db.commit()
    logger.info(f"[数据库] 已初始化 {len(plants_data)} 种植物数据")


def get_db():
    """
    获取数据库会话
    
    Yields:
        Session: 数据库会话
    """
    global _SessionLocal
    
    if _SessionLocal is None:
        init_db()
    
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 保留旧的SessionLocal引用以兼容旧代码
# 新代码应使用 get_db() 来获取会话
def get_session_local():
    """获取SessionLocal工厂函数"""
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal

# 兼容旧代码的导入 - 直接返回SessionLocal
# 使用延迟初始化确保在init_db后可用
class _SessionLocalCompat:
    """兼容旧代码的SessionLocal访问器"""
    def __call__(self):
        global _SessionLocal
        if _SessionLocal is None:
            init_db()
        return _SessionLocal()
    
    def __getattr__(self, name):
        global _SessionLocal
        if _SessionLocal is None:
            init_db()
        return getattr(_SessionLocal, name)

SessionLocal = _SessionLocalCompat()
