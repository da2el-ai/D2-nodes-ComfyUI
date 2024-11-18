import torch
import math
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
import math
from aiohttp import web
from dataclasses import dataclass
from torchvision import transforms

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
from .modules import grid_image_util


@dataclass
class D2_TAnnotation:
    title: str
    values: list

"""

D2 XY Annotation

"""
class D2_XYAnnotation:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # "type": (["STRING","INT","FLOAT",],),
                "title": ("STRING", {"default": ""}),
                "list": ("STRING", {"multiline": True},),
            },
        }
    
    RETURN_TYPES = ("D2_TAnnotation",)
    RETURN_NAMES = ("x / y_annotation",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    def run(self, title, list):
        annotation = self.__class__.get_annotation(title, list)
        return (annotation,)

    @classmethod
    def get_annotation(cls, title, list) -> D2_TAnnotation:
        array = list.strip().split('\n')
        annotation = D2_TAnnotation(title = title, values = array)
        return annotation



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
    
    RETURN_TYPES = (AnyType("*"), AnyType("*"), "D2_TAnnotation", "D2_TAnnotation", "BOOLEAN","INT",)
    RETURN_NAMES = ("X", "Y", "x_annotation", "y_annotation", "trigger","index",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"


    def run(self, x_type, x_title, x_list, y_type, y_title, y_list, auto_queue, seed, reset="", index=0):
        x_annotation = D2_XYAnnotation.get_annotation(x_type, x_title, x_list)
        y_annotation = D2_XYAnnotation.get_annotation(y_type, y_title, y_list)

        x_array = x_annotation.values
        y_array = y_annotation.values

        # 要素の数
        x_len = len(x_array)
        y_len = len(y_array)
        total = x_len * y_len

        # 採用する値
        x_value = x_array[index % x_len]
        y_value = y_array[math.floor(index / x_len)]

        # 全部完了したか
        trigger = index + 1 >= total

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


"""

D2 XY Grid Image

"""
class D2_XYGridImage:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "x_annotation": ("D2_TAnnotation", {}),
                "y_annotation": ("D2_TAnnotation", {}),
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

    image_batch = None
    finished = True

    def run(self, images, x_annotation:D2_TAnnotation, y_annotation:D2_TAnnotation, trigger, font_size, grid_gap, swap_dimensions, grid_only):
        # 完了・開始前だったら初期化する
        if self.finished:
            self.finished = False
            self.image_batch = None

        # 画像をスタックしていく
        if self.image_batch is None:
            self.image_batch = images
        else:
            self.image_batch = torch.cat((self.image_batch, images), dim=0)

        # 最後の画像まで送られたらグリッド画像生成して完了状態にする
        # 未完了なら今回送られてきた画像を送るか、または処理を止める
        if trigger:
            grid_image = self.__class__.create_grid_image(
                image_batch = self.image_batch, 
                x_annotation = x_annotation, 
                y_annotation = y_annotation, 
                font_size = font_size, 
                grid_gap = grid_gap, 
                swap_dimensions = swap_dimensions
            )
            grid_image = util.pil2tensor(grid_image)
            self.finished = True
            self.image_batch = None

            return {
                "result": (grid_image,),
            }
        elif grid_only:
            return {
                "result": (ExecutionBlocker(None),),
            }
        else:
            return {
                "result": (images,),
            }

    """
    グリッド画像作成
    """
    @classmethod
    def create_grid_image(cls, image_batch, x_annotation:D2_TAnnotation, y_annotation:D2_TAnnotation, font_size, grid_gap, swap_dimensions) -> Image.Image:
        x_len = len(x_annotation.values)
        y_len = len(y_annotation.values)

        # 見出しテキストのアイテム数から総画像数を計算
        expected_count = x_len * y_len

        # 画像数チェック
        if image_batch.shape[0] != expected_count:
            print(f"Warning: Expected {expected_count} images, but got {image_batch.shape[0]}")

        # 縦横入れ替え
        if swap_dimensions:
            x_annotation, y_annotation = y_annotation, x_annotation
            x_len, y_len = y_len, x_len

        # 見出しテキスト
        column_texts = cls.create_grid_text(x_annotation)
        row_texts = cls.create_grid_text(y_annotation)

        # テンソルからPIL Imageへの変換
        # チャンネルの位置を修正（permute使用）
        image_batch = image_batch.permute(0, 3, 1, 2)
        to_pil = transforms.ToPILImage()
        images = [to_pil(img) for img in image_batch]

        if swap_dimensions:
            grid_image = grid_image_util.create_grid_with_annotation_by_rows(
                images = images,
                gap = grid_gap,
                max_rows = len(row_texts),
                column_texts = column_texts,
                row_texts = row_texts,
                font_size = font_size
            )
        else:
            grid_image = grid_image_util.create_grid_with_annotation_by_columns(
                images = images,
                gap = grid_gap,
                max_columns = len(column_texts),
                column_texts = column_texts,
                row_texts = row_texts,
                font_size = font_size
            )

        return grid_image

    """
    アノテーション作成
    """
    @classmethod
    def create_grid_text(cls, annotation:D2_TAnnotation):
        if len(annotation.title) > 0:
            return [f"{annotation.title}: {value}" for value in annotation.values]
        else:
            return annotation.values



"""

D2 XY Checkpoint List

"""
class D2_XYCheckpointList:
    @classmethod
    def INPUT_TYPES(cls):
        ckpt_input = ["None"] +folder_paths.get_filename_list("checkpoints")
        inputs = {
            "required": {
                "ckpt_count": ("INT", {"default": 3, "min": 1, "max": 50, "step": 1}),
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
                "lora_count": ("INT", {"default": 3, "min": 1, "max": 50, "step": 1}),
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

D2 XYPromptSR2
D2 XY Plot 用に作った文字列置換

"""
class D2_XYPromptSR2:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 検索ワード
                "search": ("STRING", {}),
                # プロンプト
                "prompt": ("STRING", {"multiline":True}),
                # 置換文字列
                "x_y": ("STRING", {"forceInput":True},),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "replace_text"
    CATEGORY = "D2/XY Plot"

    def replace_text(self, prompt, search, x_y):
        new_prompt = prompt.replace(search, x_y)
        return (new_prompt,)


"""

D2 XY Seed
SEEDのリストを出力するノード

"""
class D2_XYSeed:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # プロンプト
                "seeds": ("STRING",{"multiline": True},),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("STRING", "LIST",)
    RETURN_NAMES = ("x / y_list", "LIST",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    ######
    def run(self, seeds, seed):

        # 入力文字列を改行で分割
        seed_list = seeds.strip().split('\n')

        # 出力リスト
        output_list = []

        # 入力が -1 ならランダム数値を生成
        for seed_str in seed_list:
            if seed_str == "-1":
                output_list.append(util.create_seed())
            else:
                output_list.append(int(seed_str))

        output_xy = "\n".join(str(x) for x in output_list)

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
    "D2 XY Prompt SR2": D2_XYPromptSR2,
    "D2 XY List To Plot": D2_XYListToPlot,
    "D2 XY Folder Images": D2_XYFolderImages,
    "D2 XY Seed": D2_XYSeed,
    "D2 XY Annotation": D2_XYAnnotation,
}


