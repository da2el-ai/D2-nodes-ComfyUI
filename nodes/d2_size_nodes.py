import torch
import math
import os
import json
import hashlib
import re
import random
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
import math
from aiohttp import web
from torchvision import transforms

import folder_paths
import comfy.sd
import comfy.utils
import node_helpers
import comfy.samplers
import comfy_extras.nodes_upscale_model
from comfy_execution.graph_utils import GraphBuilder
from comfy_execution.graph import ExecutionBlocker
from nodes import common_ksampler, CLIPTextEncode, PreviewImage, LoadImage, SaveImage, ControlNetApplyAdvanced
from server import PromptServer
from nodes import NODE_CLASS_MAPPINGS as nodes_NODE_CLASS_MAPPINGS

from .modules import util
from .modules import checkpoint_util
from .modules import pnginfo_util
from .modules import grid_image_util


"""

D2 Rescale Calculator
サイズのリスケール計算機

"""
class D2_ResizeCalculator:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 64, "max": 8192}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 8192}),
                "rescale_factor": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 16, "step":0.001}),
                "round_method": (["Floor", "Round", "Ceil", "None"],{"default":"Round"}),
            },
        }

    RETURN_TYPES = ("INT", "INT", "FLOAT",)
    RETURN_NAMES = ("width", "height", "rescale_factor",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, width, height, rescale_factor, round_method):

        width, height = util.resize_calc(width, height, rescale_factor, round_method)

        return(width, height, rescale_factor,)

"""

D2 Image Resize
画像リサイズ
WAS_Node_Suite の関数を流用
https://github.com/WASasquatch/was-node-suite-comfyui

"""
class D2_ImageResize:

    @classmethod
    def INPUT_TYPES(cls):
        cls.size_list, cls.size_dict = util.get_size_preset()

        return {
            "required": {
                "image": ("IMAGE",),
                "mode": (["rescale", "resize"],),
                "rescale_factor": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 16, "step":0.001}),
                "preset": (cls.size_list,),
                "resize_width": ("INT", {"default": 1024, "min": 1, "max": 48000, "step": 1}),
                "resize_height": ("INT", {"default": 1536, "min": 1, "max": 48000, "step": 1}),
                "swap_dimensions": ("BOOLEAN", {"default":False}),
                "round_method": (["Floor", "Round", "Ceil", "None"],{"default":"Round"}),
                "upscale_model": ("None", folder_paths.get_filename_list("upscale_models"), ),
                "resampling": (["lanczos", "nearest", "bilinear", "bicubic"],),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "FLOAT",)
    RETURN_NAMES = ("image", "width", "height", "rescale_factor",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(
            self, 
            image, 
            mode="rescale", 
            rescale_factor=2, 
            preset="custom", 
            resize_width=1024, 
            resize_height=1024, 
            swap_dimensions=False, 
            round_method="Floor", 
            upscale_model='None', 
            resampling="lanczos"
        ):

        scaled_images = []

        for img in image:
            resized_image, new_width, new_height = self.__class__.apply_resize_image(util.tensor2pil(img), mode, rescale_factor, resize_width, resize_height, swap_dimensions, round_method, upscale_model, resampling, preset)
            scaled_images.append(util.pil2tensor(resized_image))

        scaled_images = torch.cat(scaled_images, dim=0)

        return (scaled_images, new_width, new_height, rescale_factor, )

    """
    画像リサイズを実行
    """
    @classmethod
    def apply_resize_image(
        cls, 
        image: Image.Image, 
        mode = "rescale", 
        rescale_factor = 2, 
        resize_width = 1024, 
        resize_height = 1024, 
        swap_dimensions = False, 
        round_method = "Floor", 
        upscale_model = "None"
        resampling = "lanczos", 
        preset = "custom",
    ):
        # 最終的に仕上げるサイズ
        org_width, org_height = image.size
        new_width, new_height = cls.get_new_size(mode, rescale_factor, resize_width, resize_height, swap_dimensions, round_method, org_width, org_height, preset)

        # # Apply supersample
        # if supersample:
        #     image = image.resize((new_width * 8, new_height * 8), resample=Image.Resampling(util.RESAMPLE_FILTERS[resampling]))

        # UpscaleModelを使う
        if upscale_model != "None":
            model = size_util.load_upscale_model(upscale_model)


        # Resize the image using the given resampling filter
        resized_image = image.resize((new_width, new_height), resample=Image.Resampling(util.RESAMPLE_FILTERS[resampling]))

        return resized_image, new_width, new_height

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
    @classmethod
    def get_new_size(cls, mode="rescale", rescale_factor=2, resize_width=1024, resize_height=1024, swap_dimensions=False, round_method="Floor", org_width=0, org_height=0, preset="custom"):
        if(mode == "resize"):
            """
            数値指定モード
            """
            if(preset != "custom"):
                new_width = cls.size_dict.get(preset).get("width", resize_width)
                new_height = cls.size_dict.get(preset).get("height", resize_height)
            else:
                new_width = resize_width
                new_height = resize_height
            
            # 端数を入力される可能性があるので四捨五入
            new_width, new_height = util.resize_calc(new_width, new_height, 1, round_method)

        else:
            """
            倍率指定モード
            """
            new_width, new_height = util.resize_calc(org_width, org_height, rescale_factor, round_method)

        # 縦横入れ替え
        if swap_dimensions:
            new_width, new_height = new_height, new_width

        return new_width, new_height


"""

D2 SizeSelector
画像サイズセレクター
指定サイズの latent も取得できる

"""
class D2_SizeSelector:

    @classmethod
    def INPUT_TYPES(cls):
        # 設定を読む
        cls.size_list, cls.size_dict = util.get_size_preset()
        # config_path = util.get_config_path("sizeselector_config.yaml")
        # config_sample_path = util.get_config_path("sizeselector_config.sample.yaml")
        # config_value = util.load_config(config_path, config_sample_path)

        # cls.size_dict = config_value["size_dict"]
        # cls.size_list = ["custom"]
        # cls.size_list.extend(cls.size_dict.keys())

        return {
            "required": {
                "preset": (cls.size_list,),
                "width": ("INT", {"default": 1024, "min": 64, "max": 8192}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 8192}),
                "swap_dimensions": ("BOOLEAN", {"default":False}),
                "upscale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 16.0, "step":0.001}),
                "prescale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 16.0, "step":0.001}),
                "round_method": (["Floor", "Round", "Ceil", "None"],{"default":"Round"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64})
            },
            "optional": {
                "images": ("IMAGE",),
            },
            # "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("INT", "INT", "FLOAT", "FLOAT", "INT", "LATENT",)
    RETURN_NAMES = ("width", "height", "upscale_factor", "prescale_factor", "batch_size", "empty_latent",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, preset, width, height, swap_dimensions, upscale_factor, prescale_factor, round_method, batch_size, images=None):

        if(images != None):
            width = images.shape[2]
            height = images.shape[1]

        if(preset != "custom"):
            width = self.__class__.size_dict.get(preset).get("width", width)
            height = self.__class__.size_dict.get(preset).get("height", height)

        if swap_dimensions:
            width, height = height, width

        width, height = util.resize_calc(width, height, prescale_factor, round_method)

        latent = torch.zeros([batch_size, 4, height // 8, width // 8])

        return(width, height, upscale_factor, prescale_factor, batch_size, {"samples":latent}, )



"""

D2 Get Image Size
画像サイズ表示

"""
class D2_GetImageSize:

    @classmethod
    def INPUT_TYPES(cls):

        return {
            "required": {
                "images": ("IMAGE",),
            },
            "optional": {
                "display": ("STRING", {"multiline":True, "default":""},),
            }
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height",)
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, images, display):
        width = images.shape[2]
        height = images.shape[1]

        return {
            "result": (width, height, ),
            "ui": {
                "width": (width,), 
                "height": (height,),
            },
        }



NODE_CLASS_MAPPINGS = {
    "D2 Image Resize": D2_ImageResize,
    "D2 Resize Calculator": D2_ResizeCalculator,
    "D2 Get Image Size": D2_GetImageSize,
    "D2 Size Slector": D2_SizeSelector,
}


