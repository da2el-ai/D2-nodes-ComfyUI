from dataclasses import dataclass
from typing import Literal, Optional
import os
import yaml
# import math
import re
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

@dataclass
class D2_TAnnotation:
    title: str
    values: list

D2_TXyStatus = Literal["INIT", "FINISH", ""]

@dataclass
class D2_TD2Pipe:
    ckpt_name: str = ""
    positive: str = ""
    negative: str = ""
    seed: Optional[int] = None
    steps: Optional[int] = None
    cfg: Optional[float] = None
    sampler_name: str  = ""
    scheduler: str  = ""
    denoise: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None

@dataclass
class D2_TGridPipe:
    x_annotation: D2_TAnnotation
    y_annotation: D2_TAnnotation
    status: D2_TXyStatus



"""
seed値を作る
"""
def create_seed(num = 0):
    int_num = int(num)
    return random.randrange(MAX_SEED) if int_num == -1 else int_num


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
def load_config(config_path:Path, sample_path:Path):
    if not os.path.exists(config_path):
        shutil.copy2(sample_path, config_path)

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)



"""
ルートディレクトリ取得
"""
def get_root_path() -> Path:
    return Path(__file__).resolve().parents[2]



"""
設定ファイルのフルパスを取得
"""
def get_config_path(filename) -> Path:
    config_path = get_root_path() / 'config'
    return config_path / filename

"""
ファイルリスト取得
"""
def get_files(folder, extension) -> list[str]:
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
コメントを削除
"""
def delete_comment(text, type):
    """
    text のコメント行を消す
    type: "# only" なら行頭が「#」の行を消す
    type: "// only" なら行頭が「//」の行を消す
    type: "/* */ only" なら「/* 〜 */」を消す。これは複数行にも対応する
    type: "# + // + /**/" なら上記3つを全て実行する
    type: "None" ならなにもしない
    """
    result_text = text

    if type == "None": return text

    if type == "# only" or type == "# + // + /**/":
        # 行頭が # のコメント行を削除（行頭の空白は考慮しない）
        result_text = re.sub(r'^#.*$', '', result_text, flags=re.MULTILINE)
    
    if type == "// only" or type == "# + // + /**/":
        # 行頭が // のコメント行を削除（行頭の空白は考慮しない）
        result_text = re.sub(r'^//.*$', '', result_text, flags=re.MULTILINE)
    
    if type == "/* */ only" or type == "# + // + /**/":
        # /* */ コメントを削除（複数行対応）
        result_text = re.sub(r'/\*.*?\*/', '', result_text, flags=re.DOTALL)
    
    # # 空行が連続する場合、1つの空行にまとめる
    # result_text = re.sub(r'\n\s*\n+', '\n\n', result_text)
    
    # # 先頭と末尾の余分な改行を削除
    # result_text = result_text.strip()

    return result_text
