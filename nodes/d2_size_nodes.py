import torch

import folder_paths
from comfy_api.latest import io
# import comfy.utils
# import comfy_extras.nodes_upscale_model

from .modules import util
from .modules import size_util
from .modules import image_util


"""

D2 Rescale Calculator
サイズのリスケール計算機

"""
class D2_ResizeCalculator(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Resize Calculator",
            display_name="D2 Resize Calculator",
            category="D2",
            inputs=[
                io.Int.Input("width", default=1024, min=64, max=8192),
                io.Int.Input("height", default=1024, min=64, max=8192),
                io.Float.Input("rescale_factor", default=2.0, min=0.1, max=16, step=0.001),
                io.Combo.Input("round_method", options=["Floor", "Round", "Ceil", "None"], default="Round"),
            ],
            outputs=[
                io.Int.Output(display_name="width"),
                io.Int.Output(display_name="height"),
                io.Float.Output(display_name="rescale_factor"),
            ],
        )

    @classmethod
    def execute(cls, width, height, rescale_factor, round_method) -> io.NodeOutput:

        width, height = size_util.rescale_calc(width, height, rescale_factor, round_method)

        return io.NodeOutput(width, height, rescale_factor)


"""

D2 Image Resize
画像リサイズ
WAS_Node_Suite の関数を流用
https://github.com/WASasquatch/was-node-suite-comfyui

"""
class D2_ImageResize(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Image Resize",
            display_name="D2 Image Resize",
            category="D2",
            inputs=[
                io.Image.Input("image"),
                io.Combo.Input("mode", options=["rescale", "resize"]),
                io.Float.Input("rescale_factor", default=2.0, min=0.1, max=16, step=0.001),
                io.Combo.Input("preset", options=size_util.SIZE_LIST),
                io.Int.Input("resize_width", default=1024, min=1, max=48000, step=1),
                io.Int.Input("resize_height", default=1536, min=1, max=48000, step=1),
                io.Combo.Input("rotate", options=["None", "90 deg", "180 deg", "270 deg"]),
                io.Combo.Input("round_method", options=["Floor", "Round", "Ceil", "None"], default="Round"),
                io.Combo.Input("upscale_model", options=["None"] + folder_paths.get_filename_list("upscale_models")),
                io.Combo.Input("resampling", options=["lanczos", "nearest", "bilinear", "bicubic"]),
                io.Boolean.Input("use_tiled_vae", default=False),
                io.Mask.Input("mask", optional=True),
                io.Vae.Input("vae", optional=True),
            ],
            outputs=[
                io.Image.Output(display_name="image"),
                io.Int.Output(display_name="width"),
                io.Int.Output(display_name="height"),
                io.Float.Output(display_name="rescale_factor"),
                io.Latent.Output(display_name="latent"),
                io.Mask.Output(display_name="mask"),
            ],
        )

    @classmethod
    def execute(
            cls,
            image,
            mode = "rescale",
            rescale_factor = 2,
            preset = "custom",
            resize_width = 1024,
            resize_height = 1024,
            rotate = "None",
            round_method = "Floor",
            upscale_model = 'None',
            resampling = "lanczos",
            use_tiled_vae = False,
            mask = None,
            vae = None,
        ) -> io.NodeOutput:

        scaled_images = []
        scaled_masks = []

        # 画像のリサイズ
        for img in image:
            # 新しいサイズを取得
            new_width, new_height = size_util.get_new_size(
                mode = mode,
                rescale_factor = rescale_factor,
                resize_width = resize_width,
                resize_height = resize_height,
                round_method = round_method,
                org_width = img.shape[1],
                org_height = img.shape[0],
                preset = preset
            )

            # 回転とリサイズ
            resized_image, resized_width, resized_height = size_util.apply_resize_image(
                image_util.tensor2pil(img), 
                resize_width = new_width, 
                resize_height = new_height, 
                rotate = rotate, 
                upscale_model = upscale_model, 
                resampling = resampling, 
            )
            scaled_images.append(image_util.pil2tensor(resized_image))

        scaled_images = torch.cat(scaled_images, dim=0)

        # マスクのリサイズ
        if mask is not None:
            # バッチ次元のないマスク [H, W] を [1, H, W] に正規化
            if mask.ndim == 2:
                mask = mask.unsqueeze(0)

            for m in mask:
                # マスクをPIL Imageに変換
                mask_pil = image_util.tensor2pil(m.unsqueeze(0))

                # 新しいサイズを取得
                new_width, new_height = size_util.get_new_size(
                    mode = mode,
                    rescale_factor = rescale_factor,
                    resize_width = resize_width,
                    resize_height = resize_height,
                    round_method = round_method,
                    org_width = img.shape[1],
                    org_height = img.shape[0],
                    preset = preset
                )

                # マスクのリサイズと回転
                resized_mask, _, _ = size_util.apply_resize_mask(
                    mask_pil,
                    resize_width = new_width,
                    resize_height = new_height,
                    rotate = rotate,
                    resampling = resampling,
                )

                # マスクをテンソルに戻す
                mask_tensor = image_util.pil2tensor(resized_mask)
                scaled_masks.append(mask_tensor.squeeze(0))

            scaled_masks = torch.stack(scaled_masks, dim=0)
        else:
            scaled_masks = None

        latent = None

        if(vae is not None):
            if use_tiled_vae:
                l = vae.encode_tiled(scaled_images[:,:,:,:3])
            else:
                l = vae.encode(scaled_images[:,:,:,:3])
            latent = {"samples":l}

        return io.NodeOutput(scaled_images, resized_width, resized_height, rescale_factor, latent, scaled_masks)



"""

D2 SizeSelector
画像サイズセレクター
指定サイズの latent も取得できる

"""
class D2_SizeSelector(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Size Selector",
            display_name="D2 Size Selector",
            category="D2",
            inputs=[
                io.Combo.Input("preset", options=size_util.SIZE_LIST),
                io.Int.Input("width", default=1024, min=64, max=8192),
                io.Int.Input("height", default=1024, min=64, max=8192),
                io.Boolean.Input("swap_dimensions", default=False),
                io.Float.Input("upscale_factor", default=1.0, min=0.1, max=16.0, step=0.001),
                io.Float.Input("prescale_factor", default=1.0, min=0.1, max=16.0, step=0.001),
                io.Combo.Input("round_method", options=["Floor", "Round", "Ceil", "None"], default="Round"),
                io.Int.Input("batch_size", default=1, min=1, max=64),
                io.Image.Input("images", optional=True),
            ],
            outputs=[
                io.Int.Output(display_name="width"),
                io.Int.Output(display_name="height"),
                io.Float.Output(display_name="upscale_factor"),
                io.Float.Output(display_name="prescale_factor"),
                io.Int.Output(display_name="batch_size"),
                io.Latent.Output(display_name="empty_latent"),
            ],
        )

    @classmethod
    def execute(cls, preset, width, height, swap_dimensions, upscale_factor, prescale_factor, round_method, batch_size, images=None) -> io.NodeOutput:

        if(images != None):
            width = images.shape[2]
            height = images.shape[1]

        if(preset != "custom"):
            width = size_util.SIZE_DICT.get(preset).get("width", width)
            height = size_util.SIZE_DICT.get(preset).get("height", height)

        if swap_dimensions:
            width, height = height, width

        width, height = size_util.rescale_calc(width, height, prescale_factor, round_method)

        latent = torch.zeros([batch_size, 4, height // 8, width // 8])

        return io.NodeOutput(width, height, upscale_factor, prescale_factor, batch_size, {"samples":latent})



"""

D2 Get Image Size
画像サイズ表示

"""
class D2_GetImageSize(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Get Image Size",
            display_name="D2 Get Image Size",
            category="D2",
            inputs=[
                io.Image.Input("images"),
                io.String.Input("display", multiline=True, default="", optional=True),
            ],
            outputs=[
                io.Int.Output(display_name="width"),
                io.Int.Output(display_name="height"),
            ],
            is_output_node=True,
        )

    @classmethod
    def execute(cls, images, display="") -> io.NodeOutput:
        width = images.shape[2]
        height = images.shape[1]

        return io.NodeOutput(width, height, ui={
            "width": (width,),
            "height": (height,),
        })



NODE_CLASS_MAPPINGS = {
    "D2 Image Resize": D2_ImageResize,
    "D2 Resize Calculator": D2_ResizeCalculator,
    "D2 Get Image Size": D2_GetImageSize,
    "D2 Size Selector": D2_SizeSelector,
}
