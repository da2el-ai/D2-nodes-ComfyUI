from typing import Optional
import torch
import os
import json
# import re
import random
from PIL import Image, ImageOps, ImageSequence, ImageFile
# import numpy as np
from aiohttp import web
from torchvision import transforms
import numpy as np
# from transformers import CLIPTokenizer

import folder_paths
# import comfy.sd
# import comfy.samplers
from comfy_extras.nodes_model_advanced import RescaleCFG, ModelSamplingDiscrete

from comfy_execution.graph_utils import GraphBuilder
from comfy_execution.graph import ExecutionBlocker
# from nodes import common_ksampler, CLIPTextEncode, PreviewImage, LoadImage, SaveImage, ControlNetApplyAdvanced, LoraLoader
from nodes import LoadImage, SaveImage
from server import PromptServer
# from nodes import NODE_CLASS_MAPPINGS as nodes_NODE_CLASS_MAPPINGS

from .modules import util
# from .modules.util import D2_TD2Pipe, AnyType
# from .modules import checkpoint_util
from .modules import pnginfo_util
from .modules import grid_image_util
# from .modules.template_util import replace_template






"""

D2 Prewview Image
画像クリックでポップアップする Preview Image

"""
class D2_PreviewImage(SaveImage):
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"images": ("IMAGE", ), },
            "optional": {
                "popup_image": ("D2_PREVIEW_IMAGE", {}, )
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    CATEGORY = "D2/Image"

    def save_images(self, images, popup_image="", filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        return super().save_images(images)



"""

D2 Load Image
プロンプト出力できる Load Image

"""
class D2_LoadImage(LoadImage):

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required":{
                "image": (sorted(files), {"image_upload": True})
            },
            "optional": {
                "image_path": ("STRING", {"forceInput": True}),
                "editor": ("D2MASKEDITOR", {})
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING", "STRING" )
    RETURN_NAMES = ("IMAGE", "MASK", "width", "height", "positive", "negative")
    FUNCTION = "load_image"
    CATEGORY = "D2/Image"

    def load_image(self, image, image_path=None):

        if image_path != None:
            image = image_path
            
        # オリジナルのLoadImage処理
        output_images, output_masks = super().load_image(image)

        image_path = folder_paths.get_annotated_filepath(image)
        
        with Image.open(image_path) as img:
            width = img.size[0]
            height = img.size[1]
            prompt = pnginfo_util.get_prompt(img)
        
        return (output_images, output_masks, width, height, prompt["positive"], prompt["negative"])


"""

D2 Load Folder Images
フォルダ内画像読み込んで渡す

"""
class D2_LoadFolderImages():
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{
                "folder": ("STRING", {"default": ""}),
                "extension": ("STRING", {"default": "*.*"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    ######
    def run(self, folder = "", extension="*.*"):
        files = util.get_files(folder, extension)
        load_image = LoadImage()
        image_list = []

        for img_path in files:
            # オリジナルのLoadImage処理
            output_images, output_masks = load_image.load_image(img_path)
            image_list.append(output_images)

        image_batch = torch.cat(image_list, dim=0)
        return (image_batch,)


"""

D2 Image Stack

"""
class D2_ImageStack:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_count": ("INT", {"default": 3, "min": 1, "max": 50, "step": 1}),
            }
        }

    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "stack_image"
    CATEGORY = "D2/Image"

    def stack_image(self, image_count, **kwargs):

        image_list = []
        
        for i in range(1, image_count + 1):
            image = kwargs.get(f"image_{i}")
            if image is not None:
                image_list.append(image)

        if len(image_list) > 0:
            image_batch = torch.cat(image_list, dim=0)

            return (image_batch,)

        return (None,)

"""

D2 Folder Image Queue
フォルダ内画像の枚数分キューを送る

"""
class D2_FolderImageQueue:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required":{
                "folder": ("STRING", {"default": ""}),
                "extension": ("STRING", {"default": "*.*"}),
                "start_at": ("INT", {"default": 1}),
                "auto_queue": ("BOOLEAN", {"default": True},),
            },
            "optional": {
                "image_count": ("D2_FOLDER_IMAGE_COUNT", {})
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("image_path",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    ######
    def run(self, folder = "", extension="*.*", start_at=1, auto_queue=True, image_count=""):
        files = util.get_files(folder, extension)
        image_path = files[start_at - 1]

        return {
            "result": (image_path,),
            "ui": {
                "image_count": (len(files),),
                "start_at": (start_at,),
            }
        }





"""
対象画像枚数を取得
D2/folder-image-queue/get_image_count?folder=****&extension=***
という形式でリクエストが届く
"""
@PromptServer.instance.routes.get("/D2/folder-image-queue/get_image_count")
async def route_d2_folder_image_get_image_count(request):
    try:
        folder = request.query.get('folder')
        extension = request.query.get('extension')
        files = util.get_files(folder, extension)

        image_count = len(files)
    except:
        image_count = 0

    # JSON応答を返す
    json_data = json.dumps({"image_count":image_count})
    return web.Response(text=json_data, content_type='application/json')



"""

D2 EmptyImage Alpha
αチャンネル（透明度）付き画像作成

"""
class D2_EmptyImageAlpha:
    def __init__(self, device="cpu"):
        self.device = device

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { 
                "width": ("INT", {"default": 512, "min": 1, "max": util.MAX_RESOLUTION, "step": 1}),
                "height": ("INT", {"default": 512, "min": 1, "max": util.MAX_RESOLUTION, "step": 1}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
                "color": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFF, "step": 1, "display": "color"}),
                "alpha": ("FLOAT", {"default": 1.0, "min": 0, "max": 1.0, "step": 0.001, "display": "alpha"}),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    def run(self, width, height, batch_size=1, color=0, alpha=1.0):
        r = torch.full([batch_size, height, width, 1], ((color >> 16) & 0xFF) / 0xFF)
        g = torch.full([batch_size, height, width, 1], ((color >> 8) & 0xFF) / 0xFF)
        b = torch.full([batch_size, height, width, 1], ((color) & 0xFF) / 0xFF)
        # アルファチャンネル追加
        a = torch.full([batch_size, height, width, 1], alpha)
        # RGBAを結合
        return (torch.cat((r, g, b, a), dim=-1), )


"""

D2 Grid Image

"""
class D2_GridImage:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "max_columns": ("INT", {"default": 3},),
                "grid_gap": ("INT", {"default": 0},),
                "swap_dimensions": ("BOOLEAN", {"default": False},),
                "trigger_count": ("INT", {"default": 1, "min": 1, "step": 1}),
            },
            "optional": {
                "title_text": ("STRING", {},),
                "font_size": ("INT", {"default":24},),
                "count": ("D2_GRID_COUNT", {}),
                "reset": ("D2_GRID_RESET", {}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    TITLE_HEIGHT = 64

    def run(self, images, max_columns, grid_gap, swap_dimensions, trigger_count, title_text="", font_size=24, count=0, reset=None, unique_id=0):
        # 画像をスタックして個数を取得
        image_count = D2_GridImage_ImageStocker.add_image(unique_id, images)

        if image_count >= trigger_count:
            # グリッド画像作成
            grid_image = self.__class__.create_grid_image(
                max_columns = max_columns,
                image_batch = D2_GridImage_ImageStocker.get_images(unique_id), 
                grid_gap = grid_gap, 
                swap_dimensions = swap_dimensions
            )

            # タイトル結合
            finish_image = self.__class__.create_grid_title_image(grid_image, title_text, font_size)
            finish_image = util.pil2tensor(finish_image)
            D2_GridImage_ImageStocker.reset_images(unique_id)

            return {
                "result": (finish_image,),
                "ui": {"image_count": (image_count,),}
            }
        else:
            return {
                "result": (ExecutionBlocker(None),),
                "ui": {
                    "image_count": (image_count,),
                }
            }

    """
    グリッド＋タイトル画像作成
    """
    @classmethod
    def create_grid_title_image(cls, grid_image, title_text, font_size) -> Image.Image:
        # タイトル画像
        if len(title_text) >= 1:
            annotation_data = grid_image_util.AnnotationData(
                column_texts = [""],
                row_texts = [title_text],
                font_size = font_size
            )
            title_max_width = grid_image.size[0] - (grid_image_util.PADDING * 2)
            title_img = grid_image_util._get_text_image(annotation_data, title_text, title_max_width)
            title_height = grid_image_util.PADDING * 2 + title_img.size[1]
        else:
            title_img = Image.new('RGB', (0, 0), color=0xffffff)
            title_height = 0

        finish_height = title_height + grid_image.size[1]
        finish_img = Image.new('RGB', (grid_image.size[0], finish_height), color=0xffffff)
        finish_img.paste(title_img, (grid_image_util.PADDING, grid_image_util.PADDING))
        finish_img.paste(grid_image, (0, title_height))
        
        return finish_img


    """
    グリッド画像作成
    """
    @classmethod
    def create_grid_image(cls, image_batch, max_columns, grid_gap, swap_dimensions) -> Image.Image:
        # テンソルからPIL Imageへの変換
        # チャンネルの位置を修正（permute使用）
        image_batch = image_batch.permute(0, 3, 1, 2)
        to_pil = transforms.ToPILImage()
        images = [to_pil(img) for img in image_batch]

        if swap_dimensions:
            grid_data = grid_image_util.create_grid_by_rows(
                images = images,
                gap = grid_gap,
                max_rows = max_columns,
            )
        else:
            grid_data = grid_image_util.create_grid_by_columns(
                images = images,
                gap = grid_gap,
                max_columns = max_columns,
            )

        return grid_data.image

"""
D2 GridImage で使う、画像格納クラス
"""
class D2_GridImage_ImageStocker:
    images = {}

    @classmethod
    def get_count(cls, id:int) -> int:
        if id not in cls.images or cls.images[id] is None:
            return 0
        return cls.images[id].size(0)
    
    @classmethod
    def get_images(cls, id:int) -> Optional[torch.Tensor]:
        return cls.images[id]

    @classmethod
    def add_image(cls, id:int, image:torch.Tensor) -> int:
        if id in cls.images and cls.images[id] != None:
            cls.images[id] = torch.cat((cls.images[id], image), dim=0)
        else:
            cls.images[id] = image
        
        return cls.get_count(id)

    @classmethod
    def reset_images(cls, id:int) -> None:
        if id in cls.images:
            del cls.images[id]


"""
D2_GrodImage のストック画像をリセットする
D2/grid_image/reset_image_count?id=***
"""
@PromptServer.instance.routes.get("/D2/grid_image/reset_image_count")
async def route_d2_grid_image_reset_image_count(request):
    id = request.query.get('id')
    D2_GridImage_ImageStocker.reset_images(id)
    count = D2_GridImage_ImageStocker.get_count(id)

    # JSON応答を返す
    json_data = json.dumps({"image_count":count})
    return web.Response(text=json_data, content_type='application/json')





NODE_CLASS_MAPPINGS = {
    "D2 Preview Image": D2_PreviewImage,
    "D2 Load Image": D2_LoadImage,
    "D2 Folder Image Queue": D2_FolderImageQueue,
    # "D2 KSampler": D2_KSampler,
    # "D2 KSampler(Advanced)": D2_KSamplerAdvanced,
    # "D2 Checkpoint Loader": D2_CheckpointLoader,
    # "D2 Controlnet Loader": D2_ControlnetLoader,
    # "D2 Load Lora": D2_LoadLora,
    "D2 EmptyImage Alpha": D2_EmptyImageAlpha,
    "D2 Grid Image": D2_GridImage,
    "D2 Image Stack": D2_ImageStack,
    "D2 Load Folder Images": D2_LoadFolderImages,
    # "D2 Pipe": D2_Pipe,
}
