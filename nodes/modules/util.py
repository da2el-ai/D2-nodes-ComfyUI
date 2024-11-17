import os
import yaml
import math
import glob
import shutil
import random
from PIL import Image
import numpy as np
import torch
import latent_preview
from pathlib import Path

from comfy.cli_args import args


MAX_RESOLUTION = 16384
MAX_SEED = 0xffffffffffffffff
LINE_BREAK = "Line break"
SEPARATOR = [LINE_BREAK, ",", ";"]

RESAMPLE_FILTERS = {
    'nearest': 0,
    'bilinear': 2,
    'bicubic': 3,
    'lanczos': 1
}

"""
seed値を作る
"""
def create_seed():
    return random.randrange(MAX_SEED)


"""
入出力をANYにするもの
"""
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

"""
リストを文字結合する
"""
def list_to_text(list, separator):
    separator = "\n" if separator == "Line break" else separator
    return separator.join(list)


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
ファイルリスト取得
"""
def get_files(folder, extension):
    search_pattern = os.path.join(folder, extension)
    file_list = glob.glob(search_pattern)
    # ソートして絶対パスに変換
    file_list = sorted(file_list, key=lambda x: os.path.basename(x))
    file_list = [os.path.abspath(file) for file in file_list]
    return file_list


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
それ以外は数値そのまま返す
"""
def number_adjust(number, method='floor', target_num=8):
    valid_methods = ['round', 'ceil', 'floor', 'none']
    method = method.lower()

    if method not in valid_methods:
        raise ValueError(f"Invalid method: {method}. Must be one of {valid_methods}")

    if method == 'round':
        return round(number / target_num) * target_num
    elif method == 'ceil':
        return math.ceil(number / target_num) * target_num
    elif method == 'ceil':
        return math.floor(number / target_num) * target_num
    else:
        return number

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

"""
サイズプリセットの配列を取得
"""
def get_size_preset():
    # 設定を読む
    config_path = get_config_path("sizeselector_config.yaml")
    config_sample_path = get_config_path("sizeselector_config.sample.yaml")
    config_value = load_config(config_path, config_sample_path)

    size_dict = config_value["size_dict"]
    size_list = ["custom"]
    size_list.extend(size_dict.keys())

    return size_list, size_dict
