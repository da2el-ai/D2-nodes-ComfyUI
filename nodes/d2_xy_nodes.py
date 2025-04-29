from typing import Optional
from dataclasses import dataclass
import os
import torch
import math
import json
import re
from datetime import datetime
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
import math
from aiohttp import web
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
from .modules.util import AnyType, D2_TD2Pipe, D2_TAnnotation, D2_TXyStatus, D2_TGridPipe
from .modules import grid_image_util
from .modules import image_util






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
    def get_annotation(cls, title:str, list:str) -> D2_TAnnotation:
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
                "start_index": ("INT", {"default": 0},),
            },
            "optional": {
                "reset": ("D2_BUTTON", {"default":""}),
                "index": ("D2_XYPLOT_INDEX", {}),
                "remaining_time": ("D2_TIME", {}),
                "xy_seed": ("D2_SEED", {}),
            }

        }
    
    RETURN_TYPES = ("D2_TGridPipe", AnyType("*"), AnyType("*"), "D2_TAnnotation", "D2_TAnnotation", "STRING", "INT",)
    RETURN_NAMES = ("grid_pipe", "X", "Y", "x_annotation", "y_annotation", "status","index",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"


    def run(self, x_type, x_title, x_list, y_type, y_title, y_list, auto_queue, start_index, reset="", index=0, remaining_time=0, xy_seed=0):
        x_annotation = D2_XYAnnotation.get_annotation(x_title, x_list)
        y_annotation = D2_XYAnnotation.get_annotation(y_title, y_list)

        x_array = self.__class__.change_type(x_type, x_annotation.values)
        y_array = self.__class__.change_type(y_type, y_annotation.values)
        # 要素の数
        x_len = len(x_array)
        y_len = len(y_array)
        total = x_len * y_len

        # 採用する値
        x_value = x_array[index % x_len]
        y_value = y_array[math.floor(index / x_len)]

        # D2 Grid Image に送るステータス
        if index == 0:
            status = "INIT"
        elif index + 1 >= total:
            status = "FINISH"
        else:
            status = ""

        grid_pipe = D2_TGridPipe(
            x_annotation = x_annotation,
            y_annotation = y_annotation,
            status = status
        )

        return {
            "result": (grid_pipe, x_value, y_value, x_annotation, y_annotation, status,index,),
            "ui": {
                "auto_queue": (auto_queue,),
                "x_array": (x_array,),
                "y_array": (y_array,),
                "index": (index,),
                "total": (total,),
            }
        }

    @classmethod
    def change_type(cls, type:str, values:list) -> list:
        if type in ["INT", "steps"]:
            return [int(val) for val in values]
        elif type in ["FLOAT", "cfg", "denoise"]:
            return [float(val) for val in values]
        elif type == "seed":
            # seed値を作る
            return [util.create_seed(int(val)) for val in values]
        return values


"""

D2 XY Plot Easy

"""
class D2_XYPlotEasy:

    @classmethod
    def INPUT_TYPES(cls):
        intput_types = ["none", "positive", "negative", "ckpt_name", "seed", "steps", "cfg", "sampler_name",
                        "scheduler", "denoise", "STRING", "INT", "FLOAT",]

        return {
            "required": {
                "positive": ("STRING", {"multiline": True},),
                "negative": ("STRING", {"multiline": True},),
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "x_type": (intput_types,),
                "x_list": ("STRING", {"multiline": True},),
                "y_type": (intput_types,),
                "y_list": ("STRING", {"multiline": True},),
                "auto_queue": ("BOOLEAN", {"default": True},),
                "start_index": ("INT", {"default": 0},),
            },
            "optional": {
                "reset": ("D2_BUTTON", {"default":""}),
                "index": ("D2_XYPLOT_INDEX", {}),
                "remaining_time": ("D2_TIME", {}),
                "xy_seed": ("D2_SEED", {}),
                "progress_bar": ("D2_PROGRESS_BAR", {}),
            }
        }
   
    RETURN_TYPES = (
        "D2_TD2Pipe", "D2_TGridPipe", "STRING", "STRING", AnyType("*"), "INT", "INT", "FLOAT", AnyType("*"), AnyType("*"), "FLOAT", 
        AnyType("*"), AnyType("*"), "D2_TAnnotation", "D2_TAnnotation", "STRING", "INT",)
    RETURN_NAMES = (
        "d2_pipe", "grid_pipe", "positive", "negative", "ckpt_name", "seed", "steps", "cfg", "sampler_name", "scheduler", "denoise", 
        "x_other", "y_other", "x_annotation", "y_annotation", "status", "index",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"


    def run(self, positive, negative, ckpt_name, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index=0, reset="", index=0, remaining_time=0, xy_seed=0, progress_bar=0):
        return self.run_xy(positive, negative, ckpt_name, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index, reset, index, remaining_time, xy_seed, progress_bar, "full")


    def run_xy(self, positive, negative, ckpt_name, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index=0, reset="", index=0, remaining_time=0, xy_seed=0, progress_bar=0, mode="full"):
        
        org_values = {
            "positive": positive,
             "negative": negative,
             "ckpt_name": ckpt_name,
             "seed": seed,
             "steps": steps,
             "cfg": cfg,
             "sampler_name": sampler_name,
             "scheduler": scheduler,
             "denoise": denoise,
             "x_other": "",
             "y_other": "",
        }

        # index = 0 の時に値を変換する
        if index == 0:
            x_array = D2_XYPlot.change_type(x_type, x_list.strip().split('\n'))
            y_array = D2_XYPlot.change_type(y_type, y_list.strip().split('\n'))
            self.x_annotation = D2_TAnnotation(x_type, x_array)
            self.y_annotation = D2_TAnnotation(y_type, y_array)

        # 要素の数
        x_len = len(self.x_annotation.values)
        y_len = len(self.y_annotation.values)
        total = x_len * y_len

        # 採用する値
        x_value = self.x_annotation.values[index % x_len]
        y_value = self.y_annotation.values[math.floor(index / x_len)]

        # D2 Grid Image に送るステータス
        if index == 0:
            status = "INIT"
        elif index + 1 >= total:
            status = "FINISH"
        else:
            status = ""

        # 出力値をtypeによって変える
        org_values = self.__class__.apply_xy("x", self.x_annotation, x_value, org_values)
        org_values = self.__class__.apply_xy("y", self.y_annotation, y_value, org_values)

        # KSamplerに渡すパイプ
        d2_pipe = D2_TD2Pipe(
            positive = org_values["positive"],
            negative = org_values["negative"],
            ckpt_name = org_values["ckpt_name"],
            seed = org_values["seed"],
            steps = org_values["steps"],
            cfg = org_values["cfg"],
            sampler_name = org_values["sampler_name"],
            scheduler = org_values["scheduler"],
            denoise = org_values["denoise"],
        )

        # Grid Image に渡すパイプ
        grid_pipe = D2_TGridPipe(
            x_annotation = self.x_annotation,
            y_annotation = self.y_annotation,
            status = status
        )

        if(mode == "mini"):
            result = (
                d2_pipe,
                grid_pipe,
                org_values["positive"], org_values["negative"], org_values["ckpt_name"], 
                org_values["x_other"], org_values["y_other"], 
            )
        else:
            result = (
                d2_pipe,
                grid_pipe,
                org_values["positive"], org_values["negative"], org_values["ckpt_name"], 
                org_values["seed"], org_values["steps"], org_values["cfg"], 
                org_values["sampler_name"], org_values["scheduler"], org_values["denoise"], 
                org_values["x_other"], org_values["y_other"], 
                self.x_annotation, self.y_annotation, status,index,
            )


        return {
            "result": result,
            "ui": {
                "auto_queue": (auto_queue,),
                "x_array": (self.x_annotation.values,),
                "y_array": (self.y_annotation.values,),
                "index": (index,),
                "total": (total,),
            }
        }
    
    @classmethod
    def apply_xy(cls, xy, annotation:D2_TAnnotation, val, org_values ):
        type = annotation.title

        if type in ["ckpt_name", "steps", "cfg", "sampler_name", "scheduler", "denoise", "seed"]:
            org_values[type] = val
        elif type in ["STRING", "INT", "FLOAT"]:
            key = "x_other" if xy == "x" else "y_other"
            org_values[key] = val
        elif type == "positive" or type == "negative":
            search = annotation.values[0]
            if type == "positive":
                org_values["positive"] = cls.apply_promptsr(org_values["positive"], search, val)
            else:
                org_values["negative"] = cls.apply_promptsr(org_values["negative"], search, val)

        return org_values

    @classmethod
    def apply_promptsr(cls, prompt, search, replace):
        return prompt.replace(search, replace)



"""

D2 XY Plot Easy Mini

"""
class D2_XYPlotEasyMini(D2_XYPlotEasy):
    RETURN_TYPES = (
        "D2_TD2Pipe", "D2_TGridPipe", "STRING", "STRING", AnyType("*"), AnyType("*"), AnyType("*"),)
    RETURN_NAMES = (
        "d2_pipe", "grid_pipe", "positive", "negative", "ckpt_name", "x_other", "y_other",)

    def run(self, positive, negative, ckpt_name, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index=0, reset="", index=0, remaining_time=0, xy_seed=0, progress_bar=0):
        return self.run_xy(positive, negative, ckpt_name, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index, reset, index, remaining_time, xy_seed, progress_bar, "mini")


"""

D2 XY Grid Image

"""
class D2_XYGridImage:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "font_size": ("INT", {"default": 24},),
                "grid_gap": ("INT", {"default": 0},),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
                "grid_only": ("BOOLEAN", {"default": True},),
                "draw_x_label": ("BOOLEAN", {"default": True},),
                "draw_y_label": ("BOOLEAN", {"default": True},),
            },
            "optional": {
                "x_annotation": ("D2_TAnnotation", {}),
                "y_annotation": ("D2_TAnnotation", {}),
                "status": ("STRING", {"forceInput": True, "default": ""},),
                "grid_pipe": ("D2_TGridPipe", {"forceInput": True}),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    image_batch = None
    finished = True

    def run(self, images, font_size, grid_gap, swap_dimensions, grid_only, draw_x_label, draw_y_label,
            x_annotation:Optional[D2_TAnnotation]=None, y_annotation:Optional[D2_TAnnotation]=None, status=None, grid_pipe:Optional[D2_TGridPipe]=None):
        
        if grid_pipe != None:
            x_annotation = grid_pipe.x_annotation if grid_pipe.x_annotation else x_annotation
            y_annotation = grid_pipe.y_annotation if grid_pipe.y_annotation else y_annotation
            status = grid_pipe.status if grid_pipe.status else status

        # 最初の画像だったら初期化する
        if status == "INIT":
            self.finished = False
            self.image_batch = None

        # 画像をスタックしていく
        if self.image_batch is None:
            self.image_batch = images
        else:
            self.image_batch = torch.cat((self.image_batch, images), dim=0)

        # 最後の画像まで送られたらグリッド画像生成して完了状態にする
        # 未完了なら今回送られてきた画像を送るか、または処理を止める
        if status == "FINISH":
            grid_image = self.__class__.create_grid_image(
                image_batch = self.image_batch, 
                x_annotation = x_annotation, 
                y_annotation = y_annotation, 
                draw_x_label = draw_x_label,
                draw_y_label = draw_y_label,
                font_size = font_size, 
                grid_gap = grid_gap, 
                swap_dimensions = swap_dimensions
            )
            grid_image = image_util.pil2tensor(grid_image)
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
    def create_grid_image(
        cls, image_batch, 
        x_annotation:D2_TAnnotation, y_annotation:D2_TAnnotation, 
        draw_x_label:bool, draw_y_label:bool,
        font_size, grid_gap, swap_dimensions
    ) -> Image.Image:
        
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
            draw_x_label, draw_y_label = draw_y_label, draw_x_label

        # 見出しテキスト
        column_texts, row_texts = None, None
        if draw_x_label:
            column_texts = cls.create_grid_text(x_annotation)
        if draw_y_label:
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
                max_rows = len(y_annotation.values),
                column_texts = column_texts,
                row_texts = row_texts,
                font_size = font_size
            )
        else:
            grid_image = grid_image_util.create_grid_with_annotation_by_columns(
                images = images,
                gap = grid_gap,
                max_columns = len(x_annotation.values),
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

D2 XY Model List

"""
class D2_XYModelList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_type": (["checkpoints", "loras", "samplers", "schedulers", "upscaler", "bbox_segm"],),
                "filter": ("STRING", {"default":""}),
                "mode": (["simple", "a1111"],),
                "sort_by": (["Name", "Date"], {"default":"Name"}),
                "order_by": (["A-Z", "Z-A"], {"default":"A-Z"}),
                "get_list": ("D2_BUTTON", {}),
                "model_list": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "LIST")
    RETURN_NAMES = ("x / y_list", "LIST")
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    def run(self, model_type, filter="", mode="simple", sort_by="Name", order_by="A-Z", get_list="", model_list=""):
        list_list = model_list.split("\n")
        return (model_list, list_list,)



"""
モデルファイル一覧を取得
D2/model-list/get-list?type=****&filter=****
という形式でリクエストが届く
"""
@PromptServer.instance.routes.get("/D2/model-list/get-list")
async def route_d2_model_list_get_list(request):
    try:
        type = request.query.get('type')
        filter = request.query.get('filter')
        mode = request.query.get('mode')
        sort_by = request.query.get('sort_by')
        order_by = request.query.get('order_by')

        if type == "samplers":
            file_list = comfy.samplers.KSampler.SAMPLERS
        elif type == "schedulers":
            file_list = comfy.samplers.KSampler.SCHEDULERS
        elif type == "upscaler":
            file_list = folder_paths.get_filename_list("upscale_models")
        elif type == "bbox_segm":
            bboxs = ["bbox/"+x for x in folder_paths.get_filename_list("ultralytics_bbox")]
            segms = ["segm/"+x for x in folder_paths.get_filename_list("ultralytics_segm")]
            file_list = bboxs + segms
        else:
            file_list = folder_paths.get_filename_list(type)

        filtered_list = [s for s in file_list if re.search(filter, s, re.IGNORECASE)]

        if type in ["samplers", "schedulers", "bbox_segm", "upscaler"]:
            sorted_list = filtered_list
        else:
            model_list = []
            for file in filtered_list:
                full_path = folder_paths.get_full_path(type, file)
                # timestamp にファイルの日付を入れる
                timestamp = datetime.fromtimestamp(os.path.getmtime(full_path))

                # lora で mode:a1111 の時は <lora:〜:1> を前後に付ける
                if type == "loras" and mode == "a1111":
                    file = "<lora:" + file + ":1>"

                model_list.append({
                    'file': file,
                    'timestamp': timestamp.isoformat(),
                })

            # sort_by、order_by を使ってソートする
            reverse = order_by.lower() == 'z-a'
            sort_key = 'timestamp' if sort_by.lower() == 'date' else 'file'
            
            # fileの場合は大文字小文字を区別しないソート
            if sort_key == 'file':
                sorted_list = [item['file'] for item in sorted(model_list, key=lambda x: x[sort_key].lower(), reverse=reverse)]
            else:
                sorted_list = [item['file'] for item in sorted(model_list, key=lambda x: x[sort_key], reverse=reverse)]



    except:
        sorted_list = []

    # JSON応答を返す
    json_data = json.dumps({"files":sorted_list})
    return web.Response(text=json_data, content_type='application/json')


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

        output_xy = "\n".join([prompt.replace('\n','') for prompt in output_list])

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
                "seeds": ("STRING",{"multiline": True, "default":"-1\n-1"},),
                # "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("STRING", "LIST", AnyType("*"))
    RETURN_NAMES = ("x / y_list", "LIST", "BATCH")
    OUTPUT_IS_LIST = (False, False, True)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    ######
    def run(self, seeds):

        # 入力文字列を改行で分割
        seed_list = seeds.strip().split('\n')

        # 出力リスト
        output_list = []

        # seed値を生成
        output_list = [util.create_seed(seed) for seed in seed_list]
        output_xy = "\n".join(str(x) for x in output_list)

        return (output_xy, output_list, output_list,)


"""

D2 XY Seed 2
指定個数のSEEDのリストを出力するノード

"""
class D2_XYSeed2:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "initial_number": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
                "count": ("INT", {"default": 1, "min": 0, "max": 0xffffffffffffffff}),
                "mode": (["fixed", "increment", "decrement", "randomize"], {"default": "randomize"}),
            },
        }

    RETURN_TYPES = ("STRING", "LIST", AnyType("*"))
    RETURN_NAMES = ("x / y_list", "LIST", "BATCH")
    OUTPUT_IS_LIST = (False, False, True)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    ######
    """
    seed値を生成する
    initial_number: 元の数値
    count: 生成個数
    mode: モード（fixed / increment / decrement / randomize）
    """
    def run(self, initial_number, count, mode):
        # 出力リスト
        output_list = []
        # 初期番号生成
        initial_seed = util.create_seed(initial_number)

        # count分生成して output_list に格納
        for i in range(count):
            if(mode == "fixed"):
                output_list.append(initial_seed)
            elif(mode == "increment"):
                output_list.append(initial_seed + i)
            elif(mode == "decrement"):
                output_list.append(initial_seed - i)
            elif(mode == "randomize"):
                output_list.append(util.create_seed(-1))

        output_xy = "\n".join(str(x) for x in output_list)

        return (output_xy, output_list, output_list,)



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

D2 XY String To XYPlot

"""
class D2_XYStringToPlot:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_count": ("INT", {"default": 3, "min": 1, "max": 50, "step": 1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("x / y_list",)
    FUNCTION = "string_to_plot"
    CATEGORY = "D2/XY Plot"

    def string_to_plot(self, string_count, **kwargs):

        string_list = []
        
        for i in range(1, string_count + 1):
            string = kwargs.get(f"string_{i}")
            if string is not None:
                string_list.append(string)

        if len(string_list) > 0:
            # xy_plot は改行でアイテムを区切っているので、各アイテムの改行を消す
            cleaned = [s.replace('\n', '') for s in string_list]
            result = '\n'.join(cleaned)

            return (result,)

        return (None,)


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
                "sort_by": (["Name", "Date", "Random"], {"default":"Name"}),
                "order_by": (["A-Z", "Z-A"], {"default":"A-Z"}),
            },
            "optional": {
                "image_count": ("D2_SIMPLE_TEXT", {}),
                "queue_seed": ("D2_SEED", {}),
                "refresh_btn": ("D2_BUTTON", {})
            },
        }

    RETURN_TYPES = ("STRING", "LIST",)
    RETURN_NAMES = ("x / y_list", "LIST",)
    FUNCTION = "run"
    CATEGORY = "D2/XY Plot"

    ######
    def run(self, folder, extension, sort_by="Name", order_by="A-Z", image_count="", queue_seed=0, refresh_btn=""):
        files = util.get_files(folder, extension, sort_by, order_by)
        output = util.list_to_text(files, util.LINE_BREAK)

        return {
            "result": (output, files,),
            "ui": {
                "image_count": (len(files),),
            }
        }





NODE_CLASS_MAPPINGS = {
    "D2 XY Plot": D2_XYPlot,
    "D2 XY Plot Easy": D2_XYPlotEasy,
    "D2 XY Plot Easy Mini": D2_XYPlotEasyMini,
    "D2 XY Grid Image": D2_XYGridImage,
    "D2 XY Checkpoint List": D2_XYCheckpointList,
    "D2 XY Lora List": D2_XYLoraList,
    "D2 XY Model List": D2_XYModelList,
    "D2 XY Prompt SR": D2_XYPromptSR,
    "D2 XY Prompt SR2": D2_XYPromptSR2,
    "D2 XY List To Plot": D2_XYListToPlot,
    "D2 XY String To Plot": D2_XYStringToPlot,
    "D2 XY Folder Images": D2_XYFolderImages,
    "D2 XY Seed": D2_XYSeed,
    "D2 XY Seed2": D2_XYSeed2,
    "D2 XY Annotation": D2_XYAnnotation,
}
