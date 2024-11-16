import torch
import math
import os
import glob
import json
import hashlib
import re
import random
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
import math
from aiohttp import web

import folder_paths
import comfy.sd
import node_helpers
import comfy.samplers
from comfy_execution.graph_utils import GraphBuilder
from comfy_execution.graph import ExecutionBlocker
from nodes import common_ksampler, CLIPTextEncode, PreviewImage, LoadImage, SaveImage
from server import PromptServer

from .modules import util
from .modules.util import AnyType
from .modules import checkpoint_util
from .modules import pnginfo_util




"""

D2 XY Plot

"""
class D2_XYPlot:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_type": (["STRING","INT","FLOAT",],),
                "x_title": ("STRING", {"default": ""}),
                "x_list": ("STRING", {"multiline": True},),
                "y_type": (["STRING","INT","FLOAT",],),
                "y_title": ("STRING", {"default": ""}),
                "y_list": ("STRING", {"multiline": True},),
                "auto_queue": ("BOOLEAN", {"default": True},),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "reset": ("D2_XYPLOT_RESET", {"default":""}),
                "index": ("D2_XYPLOT_INDEX", {}),
            }

        }
    
    RETURN_TYPES = (AnyType("*"), AnyType("*"), "DICT", "DICT", "BOOLEAN","INT",)
    RETURN_NAMES = ("X", "Y", "x_annotation", "y_annotation", "trigger","index",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"


    def run(self, x_type, x_title, x_list, y_type, y_title, y_list, auto_queue, seed, reset="", index=0):
        # 入力文字列を改行で分割
        x_array = self.change_type(x_type, x_list.strip().split('\n'))
        y_array = self.change_type(y_type, y_list.strip().split('\n'))

        # 要素の数
        x_len = len(x_array)
        y_len = len(y_array)
        total = x_len * y_len

        # 採用する値
        x_value = x_array[index % x_len]
        y_value = y_array[math.floor(index / x_len)]

        # プロット図に表示する値
        x_annotation = [x_title] + x_array
        y_annotation = [y_title] + y_array

        # 全部完了したか
        trigger = index + 1 >= total

        # プロット図に表示する値
        x_annotation = {"title":x_title, "values":x_array},
        y_annotation = {"title":y_title, "values":y_array},

        return {
            "result": (x_value, y_value, x_annotation, y_annotation, trigger,index,),
            "ui": {
                "auto_queue": (auto_queue,),
                "x_array": (x_array,),
                "y_array": (y_array,),
                "index": (index,),
                "total": (total,),
            }
        }

    @classmethod
    def change_type(cls, type, values):
        outputs = []

        # 文字列を検索して置換
        for val in values:
            if type == "INT":
                outputs.append(int(val))
            elif type == "FLOAT":
                outputs.append(float(val))
            else:
                outputs.append(val)

        return outputs

"""

D2 XY Grid Image

"""
class D2_XYGridImage:

    @classmethod
    def INPUT_TYPES(cls):
        annotation = {"title":"", "values":[]}

        return {
            "required": {
                "images": ("IMAGE",),
                "x_annotation": ("DICT", {"default": annotation}),
                "y_annotation": ("DICT", {"default": annotation}),
                "trigger": ("BOOLEAN", {"forceInput": True, "default": False},),
                "font_size": ("INT", {"default": 24},),
                "grid_gap": ("INT", {"default": 0},),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
                "grid_only": ("BOOLEAN", {"default": True},),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    image_batch = torch.Tensor()
    finished = True

    def run(self, images, x_annotation, y_annotation, trigger, font_size, grid_gap, swap_dimensions, grid_only):
        if swap_dimensions:
            x_temp = x_annotation[0]
            y_temp = y_annotation[0]
            x_annotation = y_temp
            y_annotation = x_temp
        else:
            x_annotation = x_annotation[0]
            y_annotation = y_annotation[0]

        if self.finished:
            self.finished = False
            self.image_batch = torch.Tensor()

        self.image_batch = torch.cat((self.image_batch, images))

        # 期待される総画像数を計算
        expected_count = len(x_annotation['values']) * len(y_annotation['values'])

        if trigger:
            # 画像数チェック
            if self.image_batch.shape[0] != expected_count:
                print(f"Warning: Expected {expected_count} images, but got {self.image_batch.shape[0]}")
                
            # 見出しテキスト
            column_texts = self.create_grid_text(x_annotation)
            row_texts = self.create_grid_text(y_annotation)

            # images-grid-comfy-plugin を使用
            graph = GraphBuilder()
            grid_annotation_node = graph.node(
                "GridAnnotation", row_texts=row_texts, column_texts=column_texts, font_size=font_size)

            grid_node_name = "ImagesGridByColumns" if swap_dimensions else "ImagesGridByRows"

            images_grid_node = graph.node(
                grid_node_name, 
                images=self.image_batch, 
                annotation=grid_annotation_node.out(0), 
                max_columns=len(x_annotation["values"]), 
                max_rows=len(y_annotation["values"]), 
                gap=grid_gap)

            self.finished = True
            # メモリ解放
            self.image_batch = torch.Tensor()

            return {
                "result": (images_grid_node.out(0),),
                "expand": graph.finalize()
            }
        elif grid_only:
            return {
                "result": (ExecutionBlocker(None),),
            }
        else:
            return {
                "result": (images,),
            }

    @classmethod
    def create_grid_text(cls, annotation, separator=";"):
        def format_annotation(title, value):
            return value if title == "" else f"{title}:{str(value)}"

        return separator.join([
            format_annotation(annotation['title'], value)
            for value in annotation['values']
        ])



"""

D2 XY Checkpoint List

"""
class D2_XYCheckpointList:
    @classmethod
    def INPUT_TYPES(cls):
        ckpt_input = ["None"] +folder_paths.get_filename_list("checkpoints")
        inputs = {
            "required": {
                "ckpt_count": ("INT", {"default": 3, "min": 0, "max": 50, "step": 1}),
            }
        }
        for i in range(1, 50):
            inputs["required"][f"ckpt_name_{i}"] = (ckpt_input,)

        return inputs

    RETURN_TYPES = ("STRING", "LIST")
    RETURN_NAMES = ("x / y_list", "LIST")
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    def run(self, ckpt_count, **kwargs):
        ckpt_list = [kwargs.get(f"ckpt_name_{i}") for i in range(1, ckpt_count + 1)]
        ckpt_list_str = util.list_to_text(ckpt_list, util.LINE_BREAK)
        return (ckpt_list_str, ckpt_list,)


"""

D2 XY Lora List

"""
class D2_XYLoraList:
    @classmethod
    def INPUT_TYPES(cls):
        lora_input = ["None"] +folder_paths.get_filename_list("loras")
        inputs = {
            "required": {
                "lora_count": ("INT", {"default": 3, "min": 0, "max": 50, "step": 1}),
            }
        }
        for i in range(1, 50):
            inputs["required"][f"lora_name_{i}"] = (lora_input,)

        return inputs

    RETURN_TYPES = ("STRING", "LIST")
    RETURN_NAMES = ("x / y_list", "LIST")
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    def run(self, lora_count, **kwargs):
        lora_list = [kwargs.get(f"lora_name_{i}") for i in range(1, lora_count + 1)]
        lora_list_str = util.list_to_text(lora_list, util.LINE_BREAK)
        return (lora_list_str, lora_list,)


"""

D2 XYPromptSR
D2 XY Plot 用に作った文字列置換

"""
class D2_XYPromptSR:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # プロンプト
                "prompt": ("STRING", {"multiline":True, "default":""},),
                # 検索ワード
                "search": ("STRING", {"default":""}),
                # 置換文字列
                "replace": ("STRING", {"multiline":True, "default":""}),
            },
        }

    RETURN_TYPES = ("STRING", "LIST")
    RETURN_NAMES = ("x / y_list", "LIST")
    FUNCTION = "replace_text"
    CATEGORY = "D2/XY Plot"

    def replace_text(self, prompt, search, replace):
        # 置換文字列を改行で分割
        replace_items = replace.strip().split('\n')

        # 出力リスト
        output_list = [prompt]

        # 文字列を検索して置換
        for item in replace_items:
            new_prompt = prompt.replace(search, item)
            output_list.append(new_prompt)

        output_xy = "\n".join(output_list)

        return (output_xy, output_list,)



"""

D2 XY List To XYPlot

"""
class D2_XYListToPlot:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "LIST": ("LIST",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("x / y_list",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    def run(self, LIST):
        output = util.list_to_text(LIST, util.LINE_BREAK)
        return {
            "result": (output,),
        }



"""

D2 XY Folder Images
フォルダ内画像を渡す

"""
class D2_XYFolderImages:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{
                "folder": ("STRING", {"default": ""}),
                "extension": ("STRING", {"default": "*.*"}),
            },
        }

    RETURN_TYPES = ("STRING", "LIST",)
    RETURN_NAMES = ("x / y_list", "LIST",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    ######
    def run(self, folder, extension):
        files = util.get_files(folder, extension)
        output = util.list_to_text(files, util.LINE_BREAK)
        return {
            "result": (output, files,),
        }



NODE_CLASS_MAPPINGS = {
    "D2 XY Plot": D2_XYPlot,
    "D2 XY Grid Image": D2_XYGridImage,
    "D2 XY Checkpoint List": D2_XYCheckpointList,
    "D2 XY Lora List": D2_XYLoraList,
    "D2 XY Prompt SR": D2_XYPromptSR,
    "D2 XY List To Plot": D2_XYListToPlot,
    "D2 XY Folder Images": D2_XYFolderImages,
}


