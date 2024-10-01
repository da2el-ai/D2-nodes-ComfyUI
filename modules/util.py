import os
import yaml
import shutil
from pathlib import Path

"""
設定ファイルを読み込む
ファイルがなければ見本を複製する
"""
def load_config(config_path:str, sample_path:str):
    if not os.path.exists(config_path):
        shutil.copy2(sample_path, config_path)

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)



"""
ルートディレクトリ取得
"""
def get_root_path():
    return Path(__file__).resolve().parents[1]



"""
設定ファイルのフルパスを取得
"""
def get_config_path(filename):
    config_path = get_root_path() / 'config'
    return config_path / filename
    
