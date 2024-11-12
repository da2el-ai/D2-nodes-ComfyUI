import os
import yaml
import math
import shutil
from PIL import Image
import numpy as np
import torch
import latent_preview
from pathlib import Path

from comfy.cli_args import args


MAX_RESOLUTION = 16384


"""
入出力をANYにするもの
"""
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


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
    return Path(__file__).resolve().parents[2]



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

"""
任意の単位で四捨五入(round) or 切り捨て(floor) or 切り上げ(ceil)
"""
def number_adjust(number, method='floor', target_num=8):
    valid_methods = ['round', 'ceil', 'floor']
    method = method.lower()

    if method not in valid_methods:
        raise ValueError(f"Invalid method: {method}. Must be one of {valid_methods}")

    if method == 'round':
        return round(number / target_num) * target_num
    elif method == 'ceil':
        return math.ceil(number / target_num) * target_num
    else:
        return math.floor(number / target_num) * target_num

"""
幅と高さをリサイズ
"""
def resize_calc(width, height, rescale_factor=2, method='floor'):
    width = int(width*rescale_factor)
    height = int(height*rescale_factor)

    width = number_adjust(width, method, 8)
    height = number_adjust(height, method, 8)
    return width, height


"""
Tensor to PIL
"""
def tensor2pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

"""
PIL to Tensor
"""
def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)
