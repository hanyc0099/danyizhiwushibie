#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置加载模块
"""

import logging
import yaml
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"


def load_config(config_file="server_config.yaml"):
    """加载配置文件"""
    config_path = CONFIG_DIR / config_file

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 合并所有配置
    merged_config = {
        'server': config,
        'coze': load_yaml_file('coze_config.yaml'),
        'model': load_yaml_file('model_config.yaml'),
        'database': load_yaml_file('database_config.yaml')
    }

    return merged_config


def load_yaml_file(filename):
    """加载单个YAML配置文件"""
    config_path = CONFIG_DIR / filename

    if not config_path.exists():
        logger.warning(f"⚠️  配置文件不存在: {config_path}")
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# 数据库环境变量支持
def get_database_url():
    """获取数据库连接URL"""
    db_config = load_yaml_file('database_config.yaml')
    if not db_config or 'database' not in db_config:
        raise ValueError("数据库配置加载失败")

    db_mysql = db_config['database']['mysql']

    # 支持环境变量覆盖
    host = os.getenv('DB_HOST', db_mysql['host'])
    port = int(os.getenv('DB_PORT', str(db_mysql['port'])))
    user = os.getenv('DB_USER', db_mysql['user'])
    password = os.getenv('DB_PASSWORD', db_mysql['password'])
    database = os.getenv('DB_NAME', db_mysql['database'])
    charset = db_mysql.get('charset', 'utf8mb4')

    url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
    return url
