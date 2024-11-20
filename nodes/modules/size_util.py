import math
from typing import Literal
from PIL import Image
import torch
import numpy as np
# from spandrel import ModelLoader, ImageModelDescriptor
# import folder_paths
# import comfy.utils
# from comfy import model_management


from comfy_extras.nodes_upscale_model import UpscaleModelLoader, ImageUpscaleWithModel
from . import util

D2_TResizeMethod = Literal["None", "none", "Floor", "floor", "Ceil", "ceil", "Round", "round"]

RESAMPLE_FILTERS = {
    'nearest': 0,
    'bilinear': 2,
    'bicubic': 3,
    'lanczos': 1
}


"""
サイズプリセットの配列を取得
"""
def get_size_preset():
    # 設定を読む
    config_path = util.get_config_path("sizeselector_config.yaml")
    config_sample_path = util.get_config_path("sizeselector_config.sample.yaml")
    config_value = util.load_config(config_path, config_sample_path)

    size_dict = config_value["size_dict"]
    size_list = ["custom"]
    size_list.extend(size_dict.keys())

    return size_list, size_dict

SIZE_LIST, SIZE_DICT = get_size_preset()


"""
任意の単位で四捨五入(Round) or 切り捨て(Floor) or 切り上げ(Ceil)
それ以外は数値そのまま返す
"""
def number_adjust(number, method:D2_TResizeMethod='Floor', target_num=8):
    valid_methods = ['round', 'ceil', 'floor', 'none']
    lower_method = str(method).lower()

    if lower_method not in valid_methods:
        raise ValueError(f"Invalid method: {method}. Must be one of {valid_methods}")

    if lower_method == 'round':
        return round(number / target_num) * target_num
    elif lower_method == 'ceil':
        return math.ceil(number / target_num) * target_num
    elif lower_method == 'ceil':
        return math.floor(number / target_num) * target_num
    else:
        return number


"""
幅と高さをリスケール
切り下げ、切り上げ、四捨五入、何も無しを指定する
"""
def rescale_calc(width, height, rescale_factor=2, method:D2_TResizeMethod='Floor'):
    width = int(width * rescale_factor)
    height = int(height * rescale_factor)

    width = number_adjust(width, method, 8)
    height = number_adjust(height, method, 8)
    return width, height


"""
サイズ計算
mode: resize か rescale か
rescale_factor: 倍率指定
resize_width / resize_height: 数値指定
swap_dimensions: サイズの縦横を入れ替えるか
round_method: Floor / Round/ Ceil
org_width: rescale で使う変更前のサイズ（主に画像から取得）
preset: サイズプリセット
"""
def get_new_size(
        mode = "rescale", 
        rescale_factor = 2, 
        resize_width = 1024, 
        resize_height = 1024, 
        swap_dimensions = False, 
        round_method:D2_TResizeMethod = "Floor", 
        org_width = 0, 
        org_height = 0, 
        preset = "custom"
    ):

    if(mode == "resize"):
        """
        数値指定モード
        """
        if(preset != "custom"):
            new_width = SIZE_DICT.get(preset).get("width", resize_width)
            new_height = SIZE_DICT.get(preset).get("height", resize_height)
        else:
            new_width = resize_width
            new_height = resize_height
        
        # 端数を入力される可能性があるので四捨五入
        new_width, new_height = rescale_calc(new_width, new_height, 1, round_method)

    else:
        """
        倍率指定モード
        """
        new_width, new_height = rescale_calc(org_width, org_height, rescale_factor, round_method)

    # 縦横入れ替え
    if swap_dimensions:
        new_width, new_height = new_height, new_width

    return new_width, new_height



"""
画像リサイズを実行
"""
def apply_resize_image(
    image: Image.Image, 
    mode = "rescale", 
    rescale_factor = 2, 
    resize_width = 1024, 
    resize_height = 1024, 
    swap_dimensions = False, 
    round_method:D2_TResizeMethod = "Floor", 
    upscale_model = "None",
    resampling = "lanczos", 
    preset = "custom",
):
    # 最終的に仕上げるサイズ
    org_width, org_height = image.size
    new_width, new_height = get_new_size(
        mode = mode,
        rescale_factor = rescale_factor,
        resize_width = resize_width,
        resize_height = resize_height,
        swap_dimensions = swap_dimensions,
        round_method = round_method,
        org_width = org_width,
        org_height = org_height,
        preset = preset
    )
    
    # # Apply supersample
    # if supersample:
    #     image = image.resize((new_width * 8, new_height * 8), resample=Image.Resampling(util.RESAMPLE_FILTERS[resampling]))

    # # UpscaleModelを使う
    if upscale_model != "None":
        model_loader = UpscaleModelLoader()
        model = model_loader.load_model(upscale_model)[0]

        img_tensor =util.pil2tensor(image)
               
        upscaler = ImageUpscaleWithModel()
        image_tensor = upscaler.upscale(model, img_tensor)[0]

        image = util.tensor2pil(image_tensor)

    # Resize the image using the given resampling filter
    resized_image = image.resize((new_width, new_height), resample=Image.Resampling(RESAMPLE_FILTERS[resampling]))

    return resized_image, new_width, new_height


