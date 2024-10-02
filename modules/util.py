import os
import yaml
import shutil
import latent_preview
from pathlib import Path

from comfy.cli_args import args


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



"""
画像プレビューのモード切り替え
"""
def set_preview_method(method):
    if method == 'auto' or method == 'LatentPreviewMethod.Auto':
        args.preview_method = latent_preview.LatentPreviewMethod.Auto
    elif method == 'latent2rgb' or method == 'LatentPreviewMethod.Latent2RGB':
        args.preview_method = latent_preview.LatentPreviewMethod.Latent2RGB
    elif method == 'taesd' or method == 'LatentPreviewMethod.TAESD':
        args.preview_method = latent_preview.LatentPreviewMethod.TAESD
    else:
        args.preview_method = latent_preview.LatentPreviewMethod.NoPreviews

