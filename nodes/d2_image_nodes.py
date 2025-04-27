from typing import Optional
import torch
import torch.nn.functional as F
import os
import json
import random
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
from aiohttp import web
from torchvision import transforms

import folder_paths
# import comfy.sd
# import comfy.samplers
from comfy_extras.nodes_model_advanced import RescaleCFG, ModelSamplingDiscrete
from comfy.cli_args import args

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
from .modules import image_util
# from .modules import impactpack_util as impact
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
                "popup_image": ("D2_BUTTON", {}, )
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
                "editor": ("D2_BUTTON", {})
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING", "STRING", "STRING", "STRING", )
    RETURN_NAMES = ("IMAGE", "MASK", "width", "height", "positive", "negative", "filename", "filepath" )
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

        filename = os.path.basename(image_path)
        
        return (output_images, output_masks, width, height, prompt["positive"], prompt["negative"], filename, image_path)


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
            "optional": {
                "image_count": ("D2_FOLDER_IMAGE_COUNT", {}),
                "queue_seed": ("D2_FOLDER_IMAGE_SEED", {}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    ######
    def run(self, folder = "", extension="*.*", image_count="", queue_seed=0):
        files = util.get_files(folder, extension)
        load_image = LoadImage()
        image_list = []

        for img_path in files:
            # オリジナルのLoadImage処理
            output_images, output_masks = load_image.load_image(img_path)
            image_list.append(output_images)

        image_batch = torch.cat(image_list, dim=0)

        return {
            "result": (image_batch,),
            "ui": {
                "image_count": (len(files),),
            }
        }


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
            # 各画像のチャンネル数を確認
            channels = [img.shape[-1] for img in image_list]
            if len(set(channels)) > 1:
                # すべての画像を同じチャンネル数に変換
                target_channels = max(set(channels))  # 最大のチャンネル数を使用
                for i in range(len(image_list)):
                    if image_list[i].shape[-1] != target_channels:
                        if target_channels == 4 and image_list[i].shape[-1] == 3:
                            image_list[i] = image_util.convert_to_rgba_or_rgb(image_list[i], "rgba")
                        elif target_channels == 3 and image_list[i].shape[-1] == 4:
                            # RGBA -> RGB に変換（アルファチャンネルを削除）
                            image_list[i] = image_util.convert_to_rgba_or_rgb(image_list[i], "rgb")
            
            image_batch = torch.cat(image_list, dim=0)
            return (image_batch,)

        return (None,)



"""

D2 Image and Mask Stack

"""
class D2_ImageMaskStack:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_count": ("INT", {"default": 3, "min": 1, "max": 50, "step": 1}),
            }
        }

    
    RETURN_TYPES = ("IMAGE", "MASK",)
    FUNCTION = "stack_image_mask"
    CATEGORY = "D2/Image"

    def stack_image_mask(self, image_count, **kwargs):

        image_list = []
        mask_list = []
        
        for i in range(1, image_count + 1):
            image = kwargs.get(f"image_{i}")
            mask = kwargs.get(f"mask_{i}")
            if image is not None and mask is not None:
                image_list.append(image)
                mask_list.append(mask)

        if len(image_list) > 0:
            # 各画像のチャンネル数を確認
            channels = [img.shape[-1] for img in image_list]
            if len(set(channels)) > 1:
                # すべての画像を同じチャンネル数に変換
                target_channels = max(set(channels))  # 最大のチャンネル数を使用
                for i in range(len(image_list)):
                    if image_list[i].shape[-1] != target_channels:
                        if target_channels == 4 and image_list[i].shape[-1] == 3:
                            # RGB -> RGBA に変換（アルファチャンネルを1.0で追加）
                            image_list[i] = image_util.convert_to_rgba_or_rgb(image_list[i], "rgba")
                        elif target_channels == 3 and image_list[i].shape[-1] == 4:
                            # RGBA -> RGB に変換（アルファチャンネルを削除）
                            image_list[i] = image_util.convert_to_rgba_or_rgb(image_list[i], "rgb")
            
            image_batch = torch.cat(image_list, dim=0)
            mask_batch = torch.cat(mask_list, dim=0)

            return (image_batch, mask_batch,)

        return (None, None,)



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
                "start_at": ("INT", {"default": 0, "min": 0}),
                "auto_queue": ("BOOLEAN", {"default": True},),
            },
            "optional": {
                "image_count": ("D2_FOLDER_IMAGE_COUNT", {}),
                "queue_seed": ("D2_SEED", {}),
                "progress_bar": ("D2_PROGRESS_BAR", {}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("image_path",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    ######
    def run(self, folder = "", extension="*.*", start_at=1, auto_queue=True, image_count="", queue_seed=0, progress_bar=0):
        files = util.get_files(folder, extension)
        image_path = files[start_at]

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
                "red": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1}),
                "green": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1}),
                "blue": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1}),
                "alpha": ("FLOAT", {"default": 1.0, "min": 0, "max": 1.0, "step": 0.001, "display": "alpha"}),
            },
            "optional": {
                "sample": ("D2_COLOR_CANVAS", {}),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    def run(self, width, height, batch_size=1, red=0, green=0, blue=0, alpha=1.0, sample=""):
        r = torch.full([batch_size, height, width, 1], red / 255.0)
        g = torch.full([batch_size, height, width, 1], green / 255.0)
        b = torch.full([batch_size, height, width, 1], blue / 255.0)
        print("r - ", red)
        print("g - ", green)
        print("b - ", blue)
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
                "reset": ("D2_BUTTON", {}),
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
            finish_image = image_util.pil2tensor(finish_image)
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



"""

D2 Mosaic Filter
モザイクをかける

"""
class D2_MosaicFilter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { 
                "images": ("IMAGE",),
                "dot_size": ("INT", {"default": 20, "min":1, "max":512},),
                "color_mode": (["average", "original"],),
                "opacity": ("FLOAT", {"default": 1, "min":0, "max":1},),
                "brightness": ("INT", {"default": 0, "min":-100, "max":100},),
                "invert_color": ("BOOLEAN", {"default": False},),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "run"
    CATEGORY = "D2/Image"

    def run(self, images, dot_size, color_mode, opacity, brightness, invert_color):
        """
        images の画像を全てモザイク処理する
        dot_size: ドットの大きさ
        color_mode: ドットの色
            average=ドット領域の平均的な色 / original=ドット領域の中央の色 
        opacity: モザイクを重ねる時の透明度
        brightness: モザイクの明るさ。初期値:0 / -100=真っ黒 / 100=真っ白
        invert_color: 色を反転する 
        """
        
        # 結果を格納するリスト
        result_images = []
        
        # 各画像を処理
        for image in images:
            # 元の画像をコピー
            original_image = image.clone()
            
            # モザイク処理を適用
            mosaic_image = image_util.apply_mosaic_to_image(
                image, 
                dot_size, 
                color_mode, 
                brightness, 
                invert_color
            )
            
            # 元の画像とモザイク画像をopacityに基づいてブレンド
            if opacity < 1.0:
                mosaic_image = opacity * mosaic_image + (1 - opacity) * original_image
            
            # 処理した画像を結果リストに追加
            result_images.append(mosaic_image)
        
        # すべての画像を結合して返す
        return (torch.stack(result_images),)




class D2_CutByMask:
    """
    マスクから画像を切り出すノード
    class名: D2_CutByMask

    input require:
    - images: 切り出し元画像
    - mask: マスク
    - cut_type: 切り取る画像の形状
        - mask: マスクの形状通りに切り取る
        - rectangle: マスク形状から長方形を算出して切り取る
    - output_size: 出力する画像サイズ
        - mask_size: マスクのサイズ
        - image_size: 入力画像のサイズ（入力画像の位置を保持した状態で周囲が透明になる）
        - square_thumb: サムネイル用途。マスクエリアを中心に最大サイズの正方形を切り取る。padding, min_width/height は無視される

    input optional:
    - padding: マスクエリアを拡張するピクセル数（初期値 0）
    - min_width: マスクサイズの最小幅（初期値 0）
    - min_height: マスクサイズの最小高さ（初期値 0）
    - output_alpha: 出力画像にαチャンネルを含めるか

    output:
    - image: マスク領域で切り取った画像
    - mask: マスク
    - rect: 切り取った座標(x, y, width, height)
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "mask": ("MASK",),
                "cut_type": (["mask", "rectangle", "square_thumb"],),
                "output_size": (["mask_size", "image_size"],),
            },
            "optional": {
                "padding": ("INT", {"default": 0, "min": 0, "max": 1000}),
                "min_width": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "min_height": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "output_alpha": ("BOOLEAN", {"default":True})
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT",)
    RETURN_NAMES = ("image", "mask", "rect",)
    FUNCTION = "cut_by_mask"
    CATEGORY = "D2/Image"

    def cut_by_mask(self, images, mask, cut_type, output_size, padding=0, min_width=0, min_height=0, output_alpha=True):
        # ComfyUIでの画像形状: [batch, height, width, channels]
        # マスク形状: [batch, height, width] または [height, width]
        
        # 画像形状チェック - ComfyUI形式を確認
        batch_size = images.shape[0]
        height = images.shape[1]
        width = images.shape[2]
        channels = images.shape[3]
        
        # print(f"Debug - Image shape: {images.shape}, Mask shape: {mask.shape}")
        
        # ユーティリティ関数を使用してマスクを調整
        mask = image_util.adjust_mask_dimensions(mask)
        mask = image_util.check_mask_image_compatibility(mask, height, width)
        # print(f"Debug - After compatibility check: mask shape={mask.shape}")
        
        # マスクのある範囲を取得（非ゼロの部分）
        mask_np = mask.cpu().numpy()
        non_zero_indices = np.nonzero(mask_np)
        

        if cut_type == "square_thumb":
            # 正方形サムネイルモードの時は正方形でマスクを作成する
            size = min(width, height)

            if len(non_zero_indices[0]) == 0:
                # マスクがない時は中心に正方形マスクを作成
                rect = [(width - size) // 2, (height - size) // 2, size, size]
                mask = image_util.create_rectangle_mask(rect[3], rect[2], rect[0], rect[1], width, height)
            else:
                # マスクから矩形領域を作成 (paddingなどは適用しない元々のマスク範囲)
                # この関数は [x_min, y_min, rect_width, rect_height] を返す
                mask_rect = image_util.create_rectangle_from_mask(mask_np, width, height, padding=0, min_width=0, min_height=0)
                # 取得した矩形から中心座標を計算
                center_x = mask_rect[0] + mask_rect[2] // 2
                center_y = mask_rect[1] + mask_rect[3] // 2
                # 正方形
                rect = [
                    center_x - (size // 2),
                    center_y - (size // 2),
                    size, size
                ]
                # 画像範囲内に収まるように調整
                rect = image_util.adjust_rectangle_to_area(rect, width, height)

        elif len(non_zero_indices[0]) == 0:
            # マスクが空の場合、画像全体を矩形として扱う
            print("Empty mask detected, treating the entire image as the rectangle.")
            mask = image_util.create_rectangle_mask(height, width, 0, 0, width, height)
            rect = [0, 0, width, height]
            cut_type = "rectangle"
        else:
            # マスクから矩形領域を作成
            rect = image_util.create_rectangle_from_mask(mask_np, width, height, padding, min_width, min_height)
            print(f"Debug - Rect from Mask: x={rect[0]}, y={rect[1]}, width={rect[2]}, height={rect[3]}")

            # 中心座標を計算（矩形の検証に必要）
            y_min_nz, y_max_nz = non_zero_indices[0].min(), non_zero_indices[0].max()
            x_min_nz, x_max_nz = non_zero_indices[1].min(), non_zero_indices[1].max()
            center_x = (x_min_nz + x_max_nz) // 2
            center_y = (y_min_nz + y_max_nz) // 2
            # 矩形領域を検証
            rect = image_util.validate_rectangle(rect, center_x, center_y, width, height, min_width, min_height)

        # 矩形領域を取得 (この部分は共通化)
        x_min, y_min, rect_width, rect_height = rect
        # print(f"Rectangle: x={rect[0]}, y={rect[1]}, w={rect[2]}, h={rect[3]}")
        # print(f"Debug - Rect dimensions: x_min={x_min}, y_min={y_min}, rect_width={rect_width}, rect_height={rect_height}")
        
        # バッチ処理のための出力準備
        output_images = []
        
        for b in range(batch_size):
            # 2. & 3. マスクと画像のクローンを作成し、矩形領域でトリミング
            
            # 入力画像の取得 [height, width, channels]
            img = images[b]
            
            # マスクのクローン作成とトリミング [rect_height, rect_width]
            mask_crop = mask[y_min:y_min+rect_height, x_min:x_min+rect_width].clone()
            
            # 画像のクローン作成とトリミング [rect_height, rect_width, channels]
            img_crop = img[y_min:y_min+rect_height, x_min:x_min+rect_width].clone()
            
            # デバッグ情報を表示
            # print(f"Debug - Crop dimensions: mask_crop={mask_crop.shape}, img_crop={img_crop.shape}")
            
            # 4. cut_type に基づいて処理
            if cut_type == "mask":
                # マスクを画像に適用
                img_crop = image_util.apply_mask_to_image(img_crop, mask_crop)
            else:  # rectangle
                # 長方形領域を切り出す - 領域外は透明にする
                if channels != 4:  # 既にRGBA
                    # RGBをRGBAに変換
                    # 新しいRGBA画像を作成
                    rgba_img = torch.zeros((rect_height, rect_width, 4), dtype=img.dtype, device=img.device)
                    # print(f"Debug - RGBA image size: {rgba_img.shape}, img_crop size: {img_crop.shape}")
                    rgba_img[:, :, :3] = img_crop  # RGB部分をコピー
                    rgba_img[:, :, 3] = 1.0  # 矩形領域は完全不透明に
                    img_crop = rgba_img
            
            # 5. output_size に基づいて出力画像を生成
            if output_size == "mask_size":
                # トリミングした画像をそのまま使用
                output_img = img_crop
                output_mask = mask_crop
            else:  # image_size
                # 元の画像サイズに合わせた透明な画像を生成
                # RGBかRGBAかに関わらず、出力は必ずRGBAにする
                output_img = torch.zeros((height, width, 4), 
                                         dtype=img.dtype, device=img.device)
                
                # 切り抜いた画像を適切な位置に配置
                output_img[y_min:y_min+rect_height, x_min:x_min+rect_width, :] = img_crop
                
                output_mask = mask
            
            if output_alpha == False:
                output_img = image_util.convert_to_rgba_or_rgb(output_img, "rgb")

            output_images.append(output_img)
        
        # 出力を適切な形式に変換
        output_tensor = torch.stack(output_images, dim=0)
        rect_tensor = torch.tensor(rect, dtype=torch.int32)
        
        return (output_tensor, output_mask if output_size == "mask_size" else mask, rect_tensor)


class D2_PasteByMask:
    """
    マスクと領域を指定して画像を結合するノード

    input require:
    - img_base: 下地になる画像（batch対応）
    - img_paste: 貼りつける画像（batch対応）
    - paste_mode: img_paste のトリミング方法と貼り付け座標を決める
        - mask: img_paste を mask_opt でマスキングして x=0, y=0 の位置に貼りつける（マスク形状貼り付け）
        - rect_full: img_paste を rect_opt のサイズでトリミングして rect_opt の位置に貼りつける（短形貼り付け）
        - rect_position: img_paste を rect_opt の位置に貼りつける（短形貼り付け）
        - rect_pos_mask: img_paste を mask_opt でマスキングして rect_opt の位置に貼りつける（マスク形状貼り付け）
    - multi_mode: img_base, img_paste のどちらか、または両方が複数枚だった時の処理
        - pair_last: img_base, img_paste を先頭から同じインデックスのペアで処理する。片方の数が少ない時は最後の画像が採用される
        - pair_only: pair_lastと同じ。片方の数が少ない時は処理前にエラーを表示して止まる
        - cross: 全ての組み合わせを処理する

    input optional:
    - mask_opt: D2_CutByMaskが出力する mask
    - rect_opt: D2_CutByMaskが出力する rect
    - feather: 貼りつける時にエッジをボカす px数（初期値 0）

    output:
    - image: 合成した画像
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "img_base": ("IMAGE",),
                "img_paste": ("IMAGE",),
                "paste_mode": (["mask", "rect_full", "rect_position", "rect_pos_mask"],),
                "multi_mode": (["pair_last", "pair_only", "cross"],),
            },
            "optional": {
                "mask_opt": ("MASK", {"default": None, "forceInput": True}),
                "rect_opt": ("INT", {"default": None, "forceInput": True}),
                "feather": ("INT", {"default": 0, "min": 0, "max": 100}),
                "feather_type": (["simple", "distance"], {"default": "simple"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "paste_by_mask"
    CATEGORY = "D2/Image"

    def paste_by_mask(self, img_base, img_paste, paste_mode, multi_mode, mask_opt=None, rect_opt=None, feather=0, feather_type="simple"):
        """
        マスクと領域を指定して画像を結合する

        Args:
            img_base (torch.Tensor): 下地になる画像 [batch, height, width, channels]
            img_paste (torch.Tensor): 貼りつける画像 [batch, height, width, channels]
            paste_mode (str): 貼りつける方法
            multi_mode (str): 複数画像の処理方法
            mask_opt (torch.Tensor, optional): マスク [height, width] or [batch, height, width]
            rect_opt (torch.Tensor, optional): 矩形領域 [x, y, width, height]
            feather (int, optional): エッジをぼかすピクセル数
            feather_type (str, optional): フェザリングのタイプ ("simple" または "distance")

        Returns:
            torch.Tensor: 合成した画像 [batch, height, width, channels]
        """
        # 入力のチェックと調整
        batch_size_base = img_base.shape[0]
        batch_size_paste = img_paste.shape[0]
        
        base_height = img_base.shape[1]
        base_width = img_base.shape[2]
        base_channels = img_base.shape[3]
        
        paste_height = img_paste.shape[1]
        paste_width = img_paste.shape[2]
        paste_channels = img_paste.shape[3]
        
        # print(f"Debug - Base image: {img_base.shape}, Paste image: {img_paste.shape}")
        # print(f"Debug - Base batch size: {batch_size_base}, Paste batch size: {batch_size_paste}")
        # print(f"Debug - Using feather_type: {feather_type}")
        
        # マスクの調整（必要な場合）
        if mask_opt is not None:
            mask_opt = image_util.adjust_mask_dimensions(mask_opt)
            # print(f"Debimage_util.ug - Mask shape after adjustment: {mask_opt.shape}")
        
        # rect_opt の検証（ない場合は初期値を設定）
        if rect_opt is None or len(rect_opt) != 4:
            print("Rectangle not provided or invalid, using default values")
            rect_opt = torch.tensor([0, 0, paste_width, paste_height])
        
        x, y, rect_width, rect_height = rect_opt.tolist()
        # print(f"Debug - Rectangle: x={x}, y={y}, width={rect_width}, height={rect_height}")
        
        # マルチモードに応じたバッチ処理の準備
        if multi_mode == "pair_only" and batch_size_base != batch_size_paste:
            raise ValueError(f"In 'pair_only' mode, both base ({batch_size_base}) and paste ({batch_size_paste}) images must have the same batch size")
        
        output_images = []
        
        # 処理するバッチペアを決定
        if multi_mode == "cross":
            # 全ての組み合わせを処理
            batch_pairs = [(b, p) for b in range(batch_size_base) for p in range(batch_size_paste)]
        else:  # pair_last または pair_only
            # 同じインデックスのペアで処理し、少ない方の最後を繰り返す
            batch_pairs = []
            for i in range(max(batch_size_base, batch_size_paste)):
                base_idx = min(i, batch_size_base - 1)
                paste_idx = min(i, batch_size_paste - 1)
                batch_pairs.append((base_idx, paste_idx))
        
        # 各ペアを処理
        for base_idx, paste_idx in batch_pairs:
            # 各バッチの画像を取得
            img_base_single = img_base[base_idx]  # [height, width, channels]
            img_paste_single = img_paste[paste_idx]  # [height, width, channels]
            
            # 処理モードに応じた画像合成を行う
            result_img = self._process_image_pair(
                img_base_single, img_paste_single, 
                paste_mode, mask_opt, rect_opt, 
                feather, feather_type, base_height, base_width
            )
            
            output_images.append(result_img)
        
        # 出力を適切な形式に変換
        output_tensor = torch.stack(output_images, dim=0)
        return (output_tensor,)
    
    def _process_image_pair(self, img_base, img_paste, paste_mode, mask_opt, rect_opt, feather, feather_type, base_height, base_width):
        """
        1ペアの画像処理を行う
        
        Args:
            img_base (torch.Tensor): 下地画像 [height, width, channels]
            img_paste (torch.Tensor): 貼り付け画像 [height, width, channels]
            paste_mode (str): 貼りつける方法
            mask_opt (torch.Tensor): マスク
            rect_opt (torch.Tensor): 矩形領域
            feather (int): エッジをぼかすピクセル数
            feather_type (str): フェザリングのタイプ
            base_height (int): 下地画像の高さ
            base_width (int): 下地画像の幅
            
        Returns:
            torch.Tensor: 合成した画像 [height, width, channels]
        """
        # ベース画像をRGBAに変換（必要な場合）
        img_base_rgba = image_util.convert_to_rgba_or_rgb(img_base, "rgba")
        
        # 貼り付け画像の準備と変換
        img_paste_rgba = image_util.convert_to_rgba_or_rgb(img_paste, "rgba")
        
        # 矩形情報を取得
        x, y, rect_width, rect_height = rect_opt.tolist()
        
        # paste_modeに応じた処理
        if paste_mode == "mask":
            output_img = self._process_mode_mask(
                img_base_rgba, img_paste_rgba, mask_opt, 
                base_height, base_width, feather, feather_type
            )
        elif paste_mode == "rect_full":
            output_img = self._process_mode_rect_full(
                img_base_rgba, img_paste_rgba, x, y, rect_width, rect_height,
                base_height, base_width, feather, feather_type
            )
        elif paste_mode == "rect_position":
            output_img = self._process_mode_rect_position(
                img_base_rgba, img_paste_rgba, x, y, 
                base_height, base_width, feather, feather_type
            )
        elif paste_mode == "rect_pos_mask":
            output_img = self._process_mode_rect_pos_mask(
                img_base_rgba, img_paste_rgba, mask_opt, x, y, 
                base_height, base_width, feather, feather_type
            )
        else:
            raise ValueError(f"Unknown paste mode: {paste_mode}")
        return output_img


    def _process_mode_mask(self, img_base_rgba, img_paste_rgba, mask_opt, base_height, base_width, feather, feather_type):
        """マスクモード - マスクでマスキングして x=0, y=0 の位置に貼りつける"""
        if mask_opt is None:
            raise ValueError("Mask is required for 'mask' paste mode")
        
        # マスクと画像の互換性をチェック
        mask_for_paste = image_util.check_mask_image_compatibility(mask_opt, img_paste_rgba.shape[0], img_paste_rgba.shape[1])

        # マスクをフェザリング（必要な場合）
        if feather > 0:
            # 元のマスク形状を保持してフェザリング
            alpha_mask_feathered = image_util.apply_feathering(mask_for_paste.clone(), feather, feather_type)
        else:
            alpha_mask_feathered = mask_for_paste.clone() # フェザリングしない場合は元のマスク

        # 共通のアルファブレンディング処理を呼び出す
        # img_paste_rgba はマスキングせず、alpha_mask_feathered で形状を制御
        output_img = image_util.alpha_blend_paste(img_base_rgba, img_paste_rgba, alpha_mask_feathered, 0, 0)
        
        return output_img
    
    def _process_mode_rect_full(self, img_base_rgba, img_paste_rgba, x, y, rect_width, rect_height,
                              base_height, base_width, feather, feather_type):
        """短形フルモード - 貼り付けエリアのマスクを作り x=0, y=0 に貼りつける"""
        # img_paste の寸法を取得
        paste_height, paste_width = img_paste_rgba.shape[0], img_paste_rgba.shape[1]
        
        # 矩形サイズが有効かチェック
        if rect_width <= 0 or rect_height <= 0:
            print(f"Warning: Invalid rectangle dimensions: {rect_width}x{rect_height}")
            return img_base_rgba
            
        # img_paste サイズのマスクを作成
        paste_mask = image_util.create_rectangle_mask(
            height=paste_height,
            width=paste_width,
            x=x,
            y=y,
            rect_width=rect_width,
            rect_height=rect_height,
        )
        
        # マスクをフェザリング（必要な場合）
        if feather > 0:
            paste_mask = image_util.apply_feathering(paste_mask, feather, feather_type)
        
        # 共通のアルファブレンディング処理を呼び出す
        output_img = image_util.alpha_blend_paste(img_base_rgba, img_paste_rgba, paste_mask, 0, 0)
        
        return output_img

    def _process_mode_rect_position(self, img_base_rgba, img_paste_rgba, x, y,
                                  base_height, base_width, feather, feather_type):
        """
        矩形位置モード - img_paste を rect_opt の位置に貼りつける
        img_paste_rgba はトリミング済みを想定
        """
        # 貼り付け画像の寸法
        paste_height, paste_width = img_paste_rgba.shape[0], img_paste_rgba.shape[1]

        # フェザリング用のマスクを作成 (貼り付け画像のサイズで)
        paste_mask = image_util.create_rectangle_mask(
            height=paste_height,
            width=paste_width,
            x=0,
            y=0,
            rect_width=paste_width,
            rect_height=paste_height,
        )

        # マスクをフェザリング（必要な場合）
        if feather > 0:
            paste_mask = image_util.apply_feathering(paste_mask, feather, feather_type)

        # 共通のアルファブレンディング処理を呼び出す
        # 元の img_paste_rgba と paste_mask を使用し、rect_opt の x, y に貼り付け
        output_img = image_util.alpha_blend_paste(img_base_rgba, img_paste_rgba, paste_mask, x, y)

        return output_img

    def _process_mode_rect_pos_mask(self, img_base_rgba, img_paste_rgba, mask_opt, x, y,
                                   base_height, base_width, feather, feather_type):
        """
        矩形位置マスクモード - img_paste を mask_opt でマスキングして rect_opt の位置に貼りつける
        img_paste_rgba はトリミング済みを想定
        """
        if mask_opt is None:
            raise ValueError("Mask is required for 'rect_pos_mask' paste mode")

        # マスクと画像の互換性をチェック
        mask_for_paste = image_util.check_mask_image_compatibility(mask_opt, img_paste_rgba.shape[0], img_paste_rgba.shape[1])

        # マスクをフェザリング（必要な場合）
        if feather > 0:
             # 元のマスク形状を保持してフェザリング
            alpha_mask_feathered = image_util.apply_feathering(mask_for_paste.clone(), feather, feather_type)
        else:
            alpha_mask_feathered = mask_for_paste.clone() # フェザリングしない場合は元のマスク

        # 共通のアルファブレンディング処理を呼び出す
        # img_paste_rgba はマスキングせず、alpha_mask_feathered で形状を制御し、rect_opt の x, y に貼り付け
        output_img = image_util.alpha_blend_paste(img_base_rgba, img_paste_rgba, alpha_mask_feathered, x, y)

        return output_img

NODE_CLASS_MAPPINGS = {
    "D2 Preview Image": D2_PreviewImage,
    "D2 Load Image": D2_LoadImage,
    "D2 Folder Image Queue": D2_FolderImageQueue,
    "D2 EmptyImage Alpha": D2_EmptyImageAlpha,
    "D2 Grid Image": D2_GridImage,
    "D2 Image Stack": D2_ImageStack,
    "D2 Image Mask Stack": D2_ImageMaskStack,
    "D2 Load Folder Images": D2_LoadFolderImages,
    "D2 Mosaic Filter": D2_MosaicFilter,
    "D2 Cut By Mask": D2_CutByMask,
    "D2 Paste By Mask": D2_PasteByMask,
}
