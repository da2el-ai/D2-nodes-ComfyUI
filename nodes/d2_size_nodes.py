import torch

import folder_paths
# import comfy.utils
# import comfy_extras.nodes_upscale_model

from .modules import util
from .modules import size_util
from .modules import image_util


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

        width, height = size_util.rescale_calc(width, height, rescale_factor, round_method)

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
        return {
            "required": {
                "image": ("IMAGE",),
                "mode": (["rescale", "resize"],),
                "rescale_factor": ("FLOAT", {"default": 2.0, "min": 0.1, "max": 16, "step":0.001}),
                "preset": (size_util.SIZE_LIST,),
                "resize_width": ("INT", {"default": 1024, "min": 1, "max": 48000, "step": 1}),
                "resize_height": ("INT", {"default": 1536, "min": 1, "max": 48000, "step": 1}),
                "rotate": (["None", "90 deg", "180 deg", "270 deg"],),
                "round_method": (["Floor", "Round", "Ceil", "None"],{"default":"Round"}),
                "upscale_model": (["None"] + folder_paths.get_filename_list("upscale_models"), ),
                "resampling": (["lanczos", "nearest", "bilinear", "bicubic"],),
                "use_tiled_vae": ("BOOLEAN", {"default":False}),
            },
            "optional": {
                "mask": ("MASK",),
                "vae": ("VAE",),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "FLOAT", "LATENT", "MASK")
    RETURN_NAMES = ("image", "width", "height", "rescale_factor", "latent", "mask")
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(
            self, 
            image, 
            mode = "rescale", 
            rescale_factor = 2, 
            preset = "custom", 
            resize_width = 1024, 
            resize_height = 1024, 
            rotate = "None", 
            round_method:size_util.D2_TResizeMethod = "Floor", 
            upscale_model = 'None', 
            resampling = "lanczos",
            use_tiled_vae = False,
            mask = None, 
            vae = None,
        ):

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
            
            scaled_masks = torch.cat(scaled_masks, dim=0)
        else:
            scaled_masks = None

        latent = None

        if(vae is not None):
            if use_tiled_vae:
                l = vae.encode_tiled(scaled_images[:,:,:,:3])
            else:
                l = vae.encode(scaled_images[:,:,:,:3])
            latent = {"samples":l}

        return (scaled_images, resized_width, resized_height, rescale_factor, latent, scaled_masks)



"""

D2 SizeSelector
画像サイズセレクター
指定サイズの latent も取得できる

"""
class D2_SizeSelector:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (size_util.SIZE_LIST,),
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
            width = size_util.SIZE_DICT.get(preset).get("width", width)
            height = size_util.SIZE_DICT.get(preset).get("height", height)

        if swap_dimensions:
            width, height = height, width

        width, height = size_util.rescale_calc(width, height, prescale_factor, round_method)

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
