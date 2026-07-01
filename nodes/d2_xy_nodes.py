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
from comfy_api.latest import io

from .modules import util
from .modules.util import AnyType, D2_TD2Pipe, D2_TAnnotation, D2_TXyStatus, D2_TGridPipe, format_xyplot_memo
from .modules import grid_image_util
from .modules import image_util
from .modules import network_util






"""

D2 XY Annotation

"""
class D2_XYAnnotation(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Annotation",
            display_name="D2 XY Annotation",
            category="D2/XY Plot",
            inputs=[
                io.String.Input("title", default=""),
                io.String.Input("list", multiline=True),
            ],
            outputs=[
                io.Custom("D2_TAnnotation").Output(display_name="x / y_annotation"),
            ],
        )

    @classmethod
    def execute(cls, title, list) -> io.NodeOutput:
        annotation = cls.get_annotation(title, list)
        return io.NodeOutput(annotation)

    @classmethod
    def get_annotation(cls, title:str, list:str) -> D2_TAnnotation:
        array = list.strip().split('\n')
        annotation = D2_TAnnotation(title = title, values = array)
        return annotation



"""

D2 XY Plot

"""
class D2_XYPlot(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Plot",
            display_name="D2 XY Plot",
            category="D2/XY Plot",
            inputs=[
                io.Combo.Input("x_type", options=["STRING", "INT", "FLOAT"]),
                io.String.Input("x_title", default=""),
                io.String.Input("x_list", multiline=True),
                io.Combo.Input("y_type", options=["STRING", "INT", "FLOAT"]),
                io.String.Input("y_title", default=""),
                io.String.Input("y_list", multiline=True),
                io.Boolean.Input("auto_queue", default=True),
                io.Int.Input("start_index", default=0, max=65535),
                io.Custom("D2_BUTTON").Input("reset", optional=True),
                io.Custom("D2_XYPLOT_INDEX").Input("index", optional=True),
                io.Custom("D2_TIME").Input("remaining_time", optional=True),
                io.Custom("D2_SEED").Input("xy_seed", optional=True),
                io.Custom("D2_PROGRESS_BAR").Input("progress_bar", optional=True),
            ],
            outputs=[
                io.Custom("D2_TGridPipe").Output(display_name="grid_pipe"),
                io.AnyType.Output(display_name="X"),
                io.AnyType.Output(display_name="Y"),
                io.Custom("D2_TAnnotation").Output(display_name="x_annotation"),
                io.Custom("D2_TAnnotation").Output(display_name="y_annotation"),
                io.String.Output(display_name="status"),
                io.Int.Output(display_name="index"),
            ],
        )

    @classmethod
    def execute(cls, x_type, x_title, x_list, y_type, y_title, y_list, auto_queue, start_index, reset=None, index=0, remaining_time=None, xy_seed=None, progress_bar=None) -> io.NodeOutput:
        if index is None:
            index = 0
        x_annotation = D2_XYAnnotation.get_annotation(x_title, x_list)
        y_annotation = D2_XYAnnotation.get_annotation(y_title, y_list)

        x_array = cls.change_type(x_type, x_annotation.values)
        y_array = cls.change_type(y_type, y_annotation.values)
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

        return io.NodeOutput(
            grid_pipe, x_value, y_value, x_annotation, y_annotation, status, index,
            ui={
                "auto_queue": (auto_queue,),
                "x_array": (x_array,),
                "y_array": (y_array,),
                "index": (index,),
                "total": (total,),
            },
        )

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
class D2_XYPlotEasy(io.ComfyNode):
    # D2_XYPlot と同じく、x_annotation/y_annotation を index==0 のときに生成して
    # バッチ実行をまたいで再利用する（特に seed 型は create_seed(-1) でランダムになるため、
    # 同一バッチ内で同じ値を使い続ける必要がある）。V1 はインスタンス属性 self.x_annotation を
    # 使い ComfyUI の obj キャッシュ（CacheKeySetID）で再利用していたが、V3 の execute は
    # classmethod で状態を持てないため unique_id をキーにしたクラス辞書で保持する。
    _anno_state = {}

    XY_INPUT_TYPES = ["none", "positive", "negative", "ckpt_name", "seed", "steps", "cfg", "sampler_name",
                      "scheduler", "denoise", "STRING", "INT", "FLOAT"]

    @classmethod
    def _xy_inputs(cls):
        return [
            io.String.Input("positive", multiline=True),
            io.String.Input("negative", multiline=True),
            io.Combo.Input("ckpt_name", options=folder_paths.get_filename_list("checkpoints")),
            io.Combo.Input("unet_name", options=folder_paths.get_filename_list("diffusion_models")),
            io.Combo.Input("ckpt_type", options=["stable_diffusion", "diffusion"]),
            io.Int.Input("seed", default=0, min=0, max=0xffffffffffffffff),
            io.Int.Input("steps", default=20, min=1, max=10000),
            io.Float.Input("cfg", default=7.0, min=0.0, max=100.0),
            io.Combo.Input("sampler_name", options=comfy.samplers.KSampler.SAMPLERS),
            io.Combo.Input("scheduler", options=comfy.samplers.KSampler.SCHEDULERS),
            io.Float.Input("denoise", default=1.0, min=0.0, max=1.0, step=0.01),
            io.Combo.Input("x_type", options=cls.XY_INPUT_TYPES),
            io.String.Input("x_list", multiline=True),
            io.Combo.Input("y_type", options=cls.XY_INPUT_TYPES),
            io.String.Input("y_list", multiline=True),
            io.Boolean.Input("auto_queue", default=True),
            io.Int.Input("start_index", default=0, max=65535),
            io.Custom("D2_BUTTON").Input("reset", optional=True),
            io.Custom("D2_XYPLOT_INDEX").Input("index", optional=True),
            io.Custom("D2_TIME").Input("remaining_time", optional=True),
            io.Custom("D2_SEED").Input("xy_seed", optional=True),
            io.Custom("D2_PROGRESS_BAR").Input("progress_bar", optional=True),
        ]

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Plot Easy",
            display_name="D2 XY Plot Easy",
            category="D2/XY Plot",
            inputs=cls._xy_inputs(),
            outputs=[
                io.Custom("D2_TD2Pipe").Output(display_name="d2_pipe"),
                io.Custom("D2_TGridPipe").Output(display_name="grid_pipe"),
                io.String.Output(display_name="positive"),
                io.String.Output(display_name="negative"),
                io.AnyType.Output(display_name="ckpt_name"),
                io.String.Output(display_name="ckpt_type"),
                io.Int.Output(display_name="seed"),
                io.Int.Output(display_name="steps"),
                io.Float.Output(display_name="cfg"),
                io.AnyType.Output(display_name="sampler_name"),
                io.AnyType.Output(display_name="scheduler"),
                io.Float.Output(display_name="denoise"),
                io.AnyType.Output(display_name="x_other"),
                io.AnyType.Output(display_name="y_other"),
                io.Custom("D2_TAnnotation").Output(display_name="x_annotation"),
                io.Custom("D2_TAnnotation").Output(display_name="y_annotation"),
                io.String.Output(display_name="status"),
                io.Int.Output(display_name="index"),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    def execute(cls, positive, negative, ckpt_name, unet_name, ckpt_type, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index=0, reset=None, index=0, remaining_time=None, xy_seed=None, progress_bar=None) -> io.NodeOutput:
        return cls._run_xy(positive, negative, ckpt_name, unet_name, ckpt_type, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index, reset, index, remaining_time, xy_seed, progress_bar, "full")


    @classmethod
    def _run_xy(cls, positive, negative, ckpt_name, unet_name, ckpt_type, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index=0, reset=None, index=0, remaining_time=None, xy_seed=None, progress_bar=None, mode="full") -> io.NodeOutput:
        if index is None:
            index = 0

        org_values = {
            "positive": positive,
             "negative": negative,
             "ckpt_name": ckpt_name if ckpt_type == "stable_diffusion" else unet_name,
             "seed": seed,
             "steps": steps,
             "cfg": cfg,
             "sampler_name": sampler_name,
             "scheduler": scheduler,
             "denoise": denoise,
             "x_other": "",
             "y_other": "",
        }

        # index = 0 の時、またはこのノードの annotation が未生成の時に値を変換する
        # (ComfyUIはインスタンスを再生成することがあるため。状態は unique_id 毎に保持)
        state = cls._anno_state.get(cls.hidden.unique_id)
        if index == 0 or state is None:
            x_array = D2_XYPlot.change_type(x_type, x_list.strip().split('\n'))
            y_array = D2_XYPlot.change_type(y_type, y_list.strip().split('\n'))
            x_annotation = D2_TAnnotation(x_type, x_array)
            y_annotation = D2_TAnnotation(y_type, y_array)
            cls._anno_state[cls.hidden.unique_id] = {"x": x_annotation, "y": y_annotation}
        else:
            x_annotation = state["x"]
            y_annotation = state["y"]

        # 要素の数
        x_len = len(x_annotation.values)
        y_len = len(y_annotation.values)
        total = x_len * y_len

        # 採用する値
        x_value = x_annotation.values[index % x_len]
        y_value = y_annotation.values[math.floor(index / x_len)]

        # D2 Grid Image に送るステータス
        if index == 0:
            status = "INIT"
        elif index + 1 >= total:
            status = "FINISH"
        else:
            status = ""

        # 出力値をtypeによって変える
        org_values = cls.apply_xy("x", x_annotation, x_value, org_values)
        org_values = cls.apply_xy("y", y_annotation, y_value, org_values)

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
            x_annotation = x_annotation,
            y_annotation = y_annotation,
            status = status
        )

        if(mode == "mini"):
            result = (
                d2_pipe,
                grid_pipe,
                org_values["positive"], org_values["negative"], org_values["ckpt_name"], ckpt_type,
                org_values["x_other"], org_values["y_other"],
            )
        else:
            result = (
                d2_pipe,
                grid_pipe,
                org_values["positive"], org_values["negative"], org_values["ckpt_name"], ckpt_type,
                org_values["seed"], org_values["steps"], org_values["cfg"],
                org_values["sampler_name"], org_values["scheduler"], org_values["denoise"],
                org_values["x_other"], org_values["y_other"],
                x_annotation, y_annotation, status, index,
            )


        return io.NodeOutput(
            *result,
            ui={
                "auto_queue": (auto_queue,),
                "x_array": (x_annotation.values,),
                "y_array": (y_annotation.values,),
                "index": (index,),
                "total": (total,),
            },
        )

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
    # 親 D2_XYPlotEasy と出力数が違う（17→7）。V3 の RETURN_TYPES などは
    # GET_SCHEMA が `cls._RETURN_TYPES is None` のときだけ schema.outputs から構築する
    # クラス属性キャッシュ。親の GET_SCHEMA が先に走ると親の値（17出力）がキャッシュされ、
    # サブクラスは継承でその非 None 値を見て再計算をスキップしてしまう
    # （結果 y_other 等のスロット/型が親基準になり型検証で誤判定する）。
    # ここで None にリセットして Mini 自身の schema から再構築させる。
    _RETURN_TYPES = None
    _RETURN_NAMES = None
    _OUTPUT_IS_LIST = None
    _OUTPUT_TOOLTIPS = None

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Plot Easy Mini",
            display_name="D2 XY Plot Easy Mini",
            category="D2/XY Plot",
            inputs=cls._xy_inputs(),
            outputs=[
                io.Custom("D2_TD2Pipe").Output(display_name="d2_pipe"),
                io.Custom("D2_TGridPipe").Output(display_name="grid_pipe"),
                io.String.Output(display_name="positive"),
                io.String.Output(display_name="negative"),
                io.AnyType.Output(display_name="ckpt_name"),
                io.String.Output(display_name="ckpt_type"),
                io.AnyType.Output(display_name="x_other"),
                io.AnyType.Output(display_name="y_other"),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    def execute(cls, positive, negative, ckpt_name, unet_name, ckpt_type, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index=0, reset=None, index=0, remaining_time=None, xy_seed=None, progress_bar=None) -> io.NodeOutput:
        return cls._run_xy(positive, negative, ckpt_name, unet_name, ckpt_type, seed, steps, cfg, sampler_name, scheduler, denoise,
            x_type, x_list, y_type, y_list, auto_queue, start_index, reset, index, remaining_time, xy_seed, progress_bar, "mini")


"""

D2 XY Grid Image

"""
class D2_XYGridImage(io.ComfyNode):
    # V1 はインスタンス属性 self.image_batch / self.finished に画像を蓄積し、
    # ComfyUI の obj キャッシュ（CacheKeySetID）で実行間に状態を保っていた。
    # V3 の execute は classmethod で状態を持てないため、unique_id をキーにした
    # クラス辞書で per-node に保持する（V1 に hidden が無かったので unique_id を追加）。
    _grid_state = {}

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Grid Image",
            display_name="D2 XY Grid Image",
            category="D2/XY Plot",
            inputs=[
                io.Image.Input("images"),
                io.Int.Input("font_size", default=24),
                io.Int.Input("grid_gap", default=0),
                io.Boolean.Input("swap_dimensions", default=False),
                io.Boolean.Input("grid_only", default=True),
                io.Boolean.Input("draw_x_label", default=True),
                io.Boolean.Input("draw_y_label", default=True),
                io.Custom("D2_TAnnotation").Input("x_annotation", optional=True),
                io.Custom("D2_TAnnotation").Input("y_annotation", optional=True),
                # status は STRING(widget型)なので forceInput を維持。grid_pipe は
                # カスタムソケット型のため forceInput は no-op で落とす。
                io.String.Input("status", force_input=True, optional=True),
                io.Custom("D2_TGridPipe").Input("grid_pipe", optional=True),
            ],
            outputs=[
                io.Image.Output(display_name="images"),
                io.String.Output(display_name="memo"),
            ],
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    def execute(cls, images, font_size, grid_gap, swap_dimensions, grid_only, draw_x_label, draw_y_label,
            x_annotation=None, y_annotation=None, status=None, grid_pipe=None) -> io.NodeOutput:

        state = cls._grid_state.setdefault(cls.hidden.unique_id, {"image_batch": None, "finished": True})

        if grid_pipe != None:
            x_annotation = grid_pipe.x_annotation if grid_pipe.x_annotation else x_annotation
            y_annotation = grid_pipe.y_annotation if grid_pipe.y_annotation else y_annotation
            status = grid_pipe.status if grid_pipe.status else status

        # 最初の画像だったら初期化する
        if status == "INIT":
            state["finished"] = False
            state["image_batch"] = None

        # 画像をスタックしていく
        if state["image_batch"] is None:
            state["image_batch"] = images
        else:
            state["image_batch"] = torch.cat((state["image_batch"], images), dim=0)

        # 最後の画像まで送られたらグリッド画像生成して完了状態にする
        # 未完了なら今回送られてきた画像を送るか、または処理を止める
        if status == "FINISH":
            grid_image = cls.create_grid_image(
                image_batch = state["image_batch"],
                x_annotation = x_annotation,
                y_annotation = y_annotation,
                draw_x_label = draw_x_label,
                draw_y_label = draw_y_label,
                font_size = font_size,
                grid_gap = grid_gap,
                swap_dimensions = swap_dimensions
            )
            grid_image = image_util.pil2tensor(grid_image)
            state["finished"] = True
            state["image_batch"] = None

            # XY Plot のパラメータを Eagle メモ用テキストに整形して出力
            memo = format_xyplot_memo(x_annotation, y_annotation)

            return io.NodeOutput(grid_image, memo)
        elif grid_only:
            return io.NodeOutput(ExecutionBlocker(None), ExecutionBlocker(None))
        else:
            return io.NodeOutput(images, "")

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

D2 XY Model List

"""
class D2_XYModelList(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Model List",
            display_name="D2 XY Model List",
            category="D2/XY Plot",
            inputs=[
                io.Combo.Input("model_type", options=["checkpoints", "loras", "diffusion_models", "samplers", "schedulers", "upscaler", "bbox_segm", "controlnet"]),
                io.String.Input("filter", default=""),
                io.Combo.Input("mode", options=["simple", "a1111"]),
                io.Combo.Input("sort_by", options=["Name", "Date"], default="Name"),
                io.Combo.Input("order_by", options=["A-Z", "Z-A"], default="A-Z"),
                io.Custom("D2_BUTTON").Input("get_list", optional=True),
                io.String.Input("model_list", multiline=True, optional=True),
            ],
            outputs=[
                io.String.Output(display_name="x / y_list"),
                io.Custom("LIST").Output(display_name="LIST"),
            ],
        )

    @classmethod
    def execute(cls, model_type, filter="", mode="simple", sort_by="Name", order_by="A-Z", get_list=None, model_list="") -> io.NodeOutput:
        list_list = model_list.split("\n")
        return io.NodeOutput(model_list, list_list)



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
class D2_XYPromptSR(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Prompt SR",
            display_name="D2 XY Prompt SR",
            category="D2/XY Plot",
            inputs=[
                io.String.Input("prompt", multiline=True, default=""),
                io.String.Input("search", default=""),
                io.String.Input("replace", multiline=True, default=""),
            ],
            outputs=[
                io.String.Output(display_name="x / y_list"),
                io.Custom("LIST").Output(display_name="LIST"),
            ],
        )

    @classmethod
    def execute(cls, prompt, search, replace) -> io.NodeOutput:
        # 置換文字列を改行で分割
        replace_items = replace.strip().split('\n')

        # 出力リスト
        output_list = [prompt]

        # 文字列を検索して置換
        for item in replace_items:
            new_prompt = prompt.replace(search, item)
            output_list.append(new_prompt)

        output_xy = "\n".join([prompt.replace('\n','') for prompt in output_list])

        return io.NodeOutput(output_xy, output_list)



"""

D2 XYPromptSR2
D2 XY Plot 用に作った文字列置換

"""
class D2_XYPromptSR2(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Prompt SR2",
            display_name="D2 XY Prompt SR2",
            category="D2/XY Plot",
            inputs=[
                io.String.Input("search"),
                io.String.Input("prompt", multiline=True),
                io.String.Input("x_y", force_input=True),
            ],
            outputs=[
                io.String.Output(display_name="STRING"),
            ],
        )

    @classmethod
    def execute(cls, search, prompt, x_y) -> io.NodeOutput:
        new_prompt = prompt.replace(search, x_y)
        return io.NodeOutput(new_prompt)


"""

D2 XY Seed
SEEDのリストを出力するノード

"""
class D2_XYSeed(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Seed",
            display_name="D2 XY Seed",
            category="D2/XY Plot",
            inputs=[
                io.String.Input("seeds", multiline=True, default="-1\n-1"),
            ],
            outputs=[
                io.String.Output(display_name="x / y_list"),
                io.Custom("LIST").Output(display_name="LIST"),
                # V1 の OUTPUT_IS_LIST=(False, False, True) を踏襲。BATCH はリスト出力
                io.AnyType.Output(display_name="BATCH", is_output_list=True),
            ],
        )

    @classmethod
    def execute(cls, seeds) -> io.NodeOutput:

        # 入力文字列を改行で分割
        seed_list = seeds.strip().split('\n')

        # seed値を生成
        output_list = [util.create_seed(seed) for seed in seed_list]
        output_xy = "\n".join(str(x) for x in output_list)

        return io.NodeOutput(output_xy, output_list, output_list)


"""

D2 XY Seed 2
指定個数のSEEDのリストを出力するノード

"""
class D2_XYSeed2(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Seed2",
            display_name="D2 XY Seed2",
            category="D2/XY Plot",
            inputs=[
                io.Int.Input("initial_number", default=-1, min=-1, max=0xffffffffffffffff),
                io.Int.Input("count", default=1, min=0, max=0xffffffffffffffff),
                io.Combo.Input("mode", options=["fixed", "increment", "decrement", "randomize"], default="randomize"),
            ],
            outputs=[
                io.String.Output(display_name="x / y_list"),
                io.Custom("LIST").Output(display_name="LIST"),
                # V1 の OUTPUT_IS_LIST=(False, False, True) を踏襲。BATCH はリスト出力
                io.AnyType.Output(display_name="BATCH", is_output_list=True),
            ],
        )

    """
    seed値を生成する
    initial_number: 元の数値
    count: 生成個数
    mode: モード（fixed / increment / decrement / randomize）
    """
    @classmethod
    def execute(cls, initial_number, count, mode) -> io.NodeOutput:
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

        return io.NodeOutput(output_xy, output_list, output_list)



"""

D2 XY List To XYPlot

"""
class D2_XYListToPlot(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY List To Plot",
            display_name="D2 XY List To Plot",
            category="D2/XY Plot",
            inputs=[
                io.Custom("LIST").Input("LIST"),
            ],
            outputs=[
                io.String.Output(display_name="x / y_list"),
            ],
        )

    @classmethod
    def execute(cls, LIST) -> io.NodeOutput:
        output = util.list_to_text(LIST, util.LINE_BREAK)
        return io.NodeOutput(output)


"""

D2 XY String To XYPlot

"""
class D2_XYStringToPlot(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY String To Plot",
            display_name="D2 XY String To Plot",
            category="D2/XY Plot",
            inputs=[
                io.Int.Input("string_count", default=3, min=1, max=50, step=1),
            ],
            outputs=[
                io.String.Output(display_name="x / y_list"),
            ],
            # JS が string_1..N を addInput で動的追加するため **kwargs で受ける
            accept_all_inputs=True,
        )

    @classmethod
    def execute(cls, string_count, **kwargs) -> io.NodeOutput:

        string_list = []

        for i in range(1, string_count + 1):
            string = kwargs.get(f"string_{i}")
            if string is not None:
                string_list.append(string)

        if len(string_list) > 0:
            # xy_plot は改行でアイテムを区切っているので、各アイテムの改行を消す
            cleaned = [s.replace('\n', '') for s in string_list]
            result = '\n'.join(cleaned)

            return io.NodeOutput(result)

        return io.NodeOutput(None)


"""

D2 XY Folder Images
フォルダ内画像を渡す

"""
class D2_XYFolderImages(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Folder Images",
            display_name="D2 XY Folder Images",
            category="D2/XY Plot",
            inputs=[
                io.String.Input("folder", default=""),
                io.String.Input("extension", default="*.*"),
                io.Combo.Input("sort_by", options=["Name", "Date", "Random"], default="Name"),
                io.Combo.Input("order_by", options=["A-Z", "Z-A"], default="A-Z"),
                io.Custom("D2_SIMPLE_TEXT").Input("image_count", optional=True),
                io.Custom("D2_SEED").Input("queue_seed", optional=True),
                io.Custom("D2_BUTTON").Input("refresh_btn", optional=True),
            ],
            outputs=[
                io.String.Output(display_name="x / y_list"),
                io.Custom("LIST").Output(display_name="LIST"),
                io.Int.Output(display_name="image_count"),
            ],
        )

    @classmethod
    def execute(cls, folder, extension, sort_by="Name", order_by="A-Z", image_count=None, queue_seed=None, refresh_btn=None) -> io.NodeOutput:
        files = util.get_files(folder, extension, sort_by, order_by)
        output = util.list_to_text(files, util.LINE_BREAK)

        return io.NodeOutput(
            output, files, len(files),
            ui={"image_count": (len(files),)},
        )



"""

D2 Upload Image

"""
class D2_XYUploadImage(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 XY Upload Image",
            display_name="D2 XY Upload Image",
            category="D2/XY Plot",
            inputs=[
                io.String.Input("image_list", multiline=True, default=""),
                io.Custom("D2_SIMPLE_TEXT").Input("image_count", optional=True),
                io.Custom("D2_SIMPLE_TEXT").Input("status", optional=True),
            ],
            outputs=[
                io.Custom("LIST").Output(display_name="LIST"),
                io.String.Output(display_name="x / y_list"),
                io.Int.Output(display_name="image_count"),
            ],
        )

    @classmethod
    def execute(cls, image_list, image_count=0, status="") -> io.NodeOutput:
        # 入力文字列を改行で分割
        image_batch = image_list.strip().split('\n')

        return io.NodeOutput(
            image_batch, image_list, image_count,
            ui={"image_count": (len(image_batch),)},
        )




NODE_CLASS_MAPPINGS = {
    "D2 XY Plot": D2_XYPlot,
    "D2 XY Plot Easy": D2_XYPlotEasy,
    "D2 XY Plot Easy Mini": D2_XYPlotEasyMini,
    "D2 XY Grid Image": D2_XYGridImage,
    "D2 XY Model List": D2_XYModelList,
    "D2 XY Prompt SR": D2_XYPromptSR,
    "D2 XY Prompt SR2": D2_XYPromptSR2,
    "D2 XY List To Plot": D2_XYListToPlot,
    "D2 XY String To Plot": D2_XYStringToPlot,
    "D2 XY Folder Images": D2_XYFolderImages,
    "D2 XY Upload Image": D2_XYUploadImage,
    "D2 XY Seed": D2_XYSeed,
    "D2 XY Seed2": D2_XYSeed2,
    "D2 XY Annotation": D2_XYAnnotation,
}
