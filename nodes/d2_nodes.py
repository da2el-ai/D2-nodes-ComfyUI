from typing import Optional
import torch
import os
import json
import re
import random
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
from aiohttp import web
from torchvision import transforms
import numpy as np
from transformers import CLIPTokenizer

import folder_paths
import comfy.sd
import comfy.samplers
from comfy_extras.nodes_model_advanced import RescaleCFG, ModelSamplingDiscrete

from comfy_execution.graph_utils import GraphBuilder
from comfy_execution.graph import ExecutionBlocker
from nodes import common_ksampler, CLIPTextEncode, PreviewImage, LoadImage, SaveImage, ControlNetApplyAdvanced, LoraLoader
from server import PromptServer
from nodes import NODE_CLASS_MAPPINGS as nodes_NODE_CLASS_MAPPINGS

from .modules import util
from .modules.util import D2_TD2Pipe, AnyType
from .modules import checkpoint_util
from .modules import pnginfo_util
from .modules import grid_image_util
from .modules.template_util import replace_template




"""
Controlnet object wrapper
"""
class D2_Cnet:
    def __init__(self, controlnet_name, image, strength, start_percent, end_percent):
        self.controlnet_path = folder_paths.get_full_path_or_raise("controlnet", controlnet_name)
        self.controlnet = comfy.controlnet.load_controlnet(self.controlnet_path)
        self.image = image
        self.strength = strength
        self.start_percent = start_percent
        self.end_percent = end_percent





"""

D2 KSampler
positive / negative 入力に文字列が使える KSampler

"""
class D2_KSampler:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                "latent_image": ("LATENT",),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "preview_method": (["auto", "latent2rgb", "taesd", "vae_decoded_only", "none"],),
                "positive": ("STRING", {"default": "","multiline": True}),
                "negative": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "cnet_stack": ("D2_CNET_STACK",),
                "d2_pipe": ("D2_TD2Pipe",),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("IMAGE", "LATENT", "MODEL", "CLIP", "STRING", "STRING", "STRING", "CONDITIONING", "CONDITIONING", "D2_TD2Pipe", )
    RETURN_NAMES = ("IMAGE", "LATENT", "MODEL", "CLIP", "positive", "formated_positive", "negative", "positive_cond", "negative_cond", "d2_pipe", )
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"


    def run(self, model, clip, vae, seed, steps, cfg, sampler_name, scheduler, latent_image, denoise, 
            preview_method, positive, negative, positive_cond=None, negative_cond=None, cnet_stack=None, 
            d2_pipe:Optional[D2_TD2Pipe]=None, prompt=None, extra_pnginfo=None, my_unique_id=None,
            add_noise=None, start_at_step=None, end_at_step=None, return_with_leftover_noise=None, sampler_type="regular"):

        util.set_preview_method(preview_method)

        # positive / negative 以外は pipe を優先する
        if d2_pipe == None:
            d2_pipe = D2_TD2Pipe(
                positive = positive,
                negative = negative,
                seed = seed,
                steps = steps,
                cfg = cfg,
                sampler_name = sampler_name,
                scheduler = scheduler,
                denoise = denoise,
            )
        else:
            if not d2_pipe.positive:
                d2_pipe.positive = positive
            if not d2_pipe.negative:
                d2_pipe.negative = negative

        # lora 適用を試みる
        lora_params, formated_positive = D2_LoadLora.get_params_a1111(d2_pipe.positive)
        lora_model, lora_clip = D2_LoadLora.apply_lora(model, clip, lora_params)

        # コンディショニングが入力されていたらそちらを優先する
        if positive_cond != None:
            positive_encoded = positive_cond
        else:
            (positive_encoded,) = CLIPTextEncode().encode(lora_clip, formated_positive)
        
        if negative_cond != None:
            negative_encoded = negative_cond
        else:
            (negative_encoded,) = CLIPTextEncode().encode(lora_clip, d2_pipe.negative)

        # control net
        if isinstance(cnet_stack, list):
            for d2_cnet in cnet_stack:
                controlnet_conditioning = ControlNetApplyAdvanced().apply_controlnet(
                    positive_encoded, negative_encoded, 
                    d2_cnet.controlnet, d2_cnet.image, d2_cnet.strength,
                    d2_cnet.start_percent, d2_cnet.end_percent
                )
                positive_encoded, negative_encoded = controlnet_conditioning[0], controlnet_conditioning[1]

        disable_noise = add_noise == "disable"
        force_full_denoise = return_with_leftover_noise != "enable"

        # KSampler実行
        latent = common_ksampler(
            lora_model, d2_pipe.seed, d2_pipe.steps, d2_pipe.cfg, d2_pipe.sampler_name, d2_pipe.scheduler, 
            positive_encoded, negative_encoded, latent_image, 
            denoise=d2_pipe.denoise, disable_noise=disable_noise, 
            start_step=start_at_step, last_step=end_at_step, force_full_denoise=force_full_denoise
        )[0]

        latent_samples = latent['samples']
        samp_images = vae.decode(latent_samples).cpu()
        results_images = PreviewImage().save_images(samp_images, "d2", prompt, extra_pnginfo)['ui']['images']

        return {
            "ui": {"images": results_images},
            "result": (samp_images, latent, lora_model, lora_clip, d2_pipe.positive, formated_positive, d2_pipe.negative, positive_encoded, negative_encoded, d2_pipe, )
        }



"""

D2 KSampler(Advanced)
positive / negative 入力に文字列が使える KSampler Advanced

"""
class D2_KSamplerAdvanced(D2_KSampler):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "add_noise": (["enable", "disable"],),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                "latent_image": ("LATENT",),
                "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                "return_with_leftover_noise": (["disable", "enable"],),
                "preview_method": (["auto", "latent2rgb", "taesd", "vae_decoded_only", "none"],),
                "positive": ("STRING", {"default": "","multiline": True}),
                "negative": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "positive_cond": ("CONDITIONING",),
                "negative_cond": ("CONDITIONING",),
                "cnet_stack": ("D2_CNET_STACK",),
                "d2_pipe": ("D2_TD2Pipe",),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("IMAGE", "LATENT", "MODEL", "CLIP", "STRING", "STRING", "STRING", "CONDITIONING", "CONDITIONING", "D2_TD2Pipe", )
    RETURN_NAMES = ("IMAGE", "LATENT", "MODEL", "CLIP", "positive", "formated_positive", "negative", "positive_cond", "negative_cond", "d2_pipe", )

    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, model, clip, vae, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, latent_image, 
            start_at_step, end_at_step, return_with_leftover_noise,
            preview_method, positive, negative, positive_cond=None, negative_cond=None, cnet_stack=None, d2_pipe=None, prompt=None, extra_pnginfo=None, my_unique_id=None, denoise=1.0):

        return super().run(model, clip, vae, noise_seed, steps, cfg, sampler_name, scheduler, latent_image, denoise,
            preview_method, positive, negative, positive_cond, negative_cond, cnet_stack, d2_pipe, prompt, extra_pnginfo, my_unique_id,
            add_noise, start_at_step, end_at_step, return_with_leftover_noise, sampler_type="advanced")




"""

D2_CheckpointLoader
Checkpointのフルパスを取得できる Checkpoint Loader

"""
class D2_CheckpointLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                "auto_vpred": ("BOOLEAN", {"default": True}),
                "sampling": (["normal", "eps", "v_prediction", "lcm", "x0"],),
                "zsnr": ("BOOLEAN", {"default": False}),
                "multiplier": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID", "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT"}
            }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "STRING", "STRING", "STRING",)
    RETURN_NAMES = ("model", "clip", "vae", "ckpt_name", "ckpt_hash", "ckpt_fullpath", "sampling", )
    FUNCTION = "load_checkpoint"

    CATEGORY = "D2"

    def load_checkpoint(
            self, 
            ckpt_name, 
            auto_vpred = True, 
            sampling = "normal", 
            zsnr = False, 
            multiplier = 0.6, 
            output_vae = True, 
            output_clip = True, 
            unique_id = None, 
            extra_pnginfo = None, 
            prompt = None
        ):
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        model = out[0]
        clip = out[1]
        vae = out[2]

        # vpred対応準備
        model_sampling = ModelSamplingDiscrete()
        rescale_cfg = RescaleCFG()

        if auto_vpred and "vpred" in ckpt_name.lower():
            sampling = "v_prediction"
            model = model_sampling.patch(model, "v_prediction", zsnr)[0]
            model = rescale_cfg.patch(model, multiplier)[0]

        elif sampling != "normal":
            model = model_sampling.patch(model, sampling, zsnr)[0]
            model = rescale_cfg.patch(model, multiplier)[0]

        hash = checkpoint_util.get_file_hash(ckpt_path)
        ckpt_name = os.path.basename(ckpt_name)
        return (model, clip, vae, ckpt_name, hash, ckpt_path, sampling,)




"""

D2 Controlnet Loader
D2 Ksampler専用のcontrolnetローダー

"""
class D2_ControlnetLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { 
                "controlnet_name": (folder_paths.get_filename_list("controlnet"),),
                "image": ("IMAGE",),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.001}),
                "start_percent": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.001}),
                "end_percent": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.001})
            },
            "optional": {
                "cnet_stack": ("D2_CNET_STACK",),
            },
        }

    RETURN_TYPES = ("D2_CNET_STACK",)
    RETURN_NAMES = ("cnet_stack",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, controlnet_name, image, strength, start_percent, end_percent, cnet_stack=None ):
        d2_cnet = D2_Cnet(
            controlnet_name, image, strength, start_percent, end_percent
        )

        if isinstance(cnet_stack, list):
            cnet_stack.append(d2_cnet)
        else:
            cnet_stack = [d2_cnet]
        
        return (cnet_stack,)



"""

D2 Load Lora
Loraの指定をテキストで行うノード

"""
class D2_LoadLora:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_text": ("STRING", {"multiline": True}),
                "mode": (["a1111", "simple"],),
                "insert_lora": (["CHOOSE"] + folder_paths.get_filename_list("loras"),)
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING",)
    RETURN_NAMES = ("MODEL", "CLIP", "prompt", "formated_prompt",)
    FUNCTION = "run"
    CATEGORY = "D2"

    ######
    def run(self, model, clip, lora_text, mode, insert_lora):
        if mode == "simple":
            processed_params = self.__class__.get_params_simple(lora_text)
            formated_text = ""
        else:
            processed_params, formated_text = self.__class__.get_params_a1111(lora_text)

        model, clip = self.__class__.apply_lora(model, clip, processed_params)

        return (model, clip, lora_text, formated_text,)

    ######
    @classmethod
    def apply_lora(cls, model, clip, lora_params):
        """
        Loraを適用する

        - lora_param: {lora_path}:{strength_model}:{strength_clip}
        strength_clip が存在しない場合は strength_model と同じ値が適用される
        strength_model が存在しない場合は strength_model / strength_clip 両方に「1」が適用される
        """
        for lora_param in lora_params:

            # パラメータを分割
            parts = lora_param.split(':')
            lora_name = parts[0].strip()
            
            # strength_model と strength_clip の設定
            if len(parts) > 1:
                strength_model = float(parts[1].strip())
            else:
                strength_model = 1.0
                
            if len(parts) > 2:
                strength_clip = float(parts[2].strip())
            else:
                strength_clip = strength_model
                
            # LoraLoader を使用して lora を適用
            lora_loader = LoraLoader()
            model, clip = lora_loader.load_lora(model, clip, lora_name, strength_model, strength_clip)

        return model, clip

    # シンプルモード
    @classmethod
    def get_params_simple(cls, lora_text):
        """
        LoRAパラメーターを返す
        lora_text は下記のフォーマットのテキスト
        -----------
        {lora_name}:{strength_model}:{strength_clip}
        {lora_name}:{strength_model}:{strength_clip},{lora_name}:{strength_model}:{strength_clip}
        -----------
        先頭が「#」または「//」で始まるものはコメントとして無視する
        """
        processed_params = []

        # 入力文字列を改行で分割
        params = lora_text.strip().split('\n')

        # 文字列を検索して置換
        for lora_param in params:
            
            # コメント行をスキップ
            if lora_param.startswith('#') or lora_param.startswith('//') or not lora_param.strip():
                continue

            # カンマで分割して処理対象リストに追加
            sub_params = lora_param.split(',')
            for sub_param in sub_params:
                if sub_param.strip():  # 空でない場合のみ追加
                    processed_params.append(sub_param.strip())

        return processed_params

    # A1111モード
    @classmethod
    def get_params_a1111(cls, lora_text):
        """
        LoRAパラメーターを返す
        lora_text は下記のフォーマットのテキスト
        A1111のようにプロンプトの中に <〜> でLoRAパラメータが記載されている
        -----------
        promptA, promptB, promptC,
        <lora:{lora_name}>, promptX,
        <lora:{lora_name}:{strength_model}>
        <lora:{lora_name}:{strength_model}:{strength_clip}>
        promptY,
        -----------
        """
        processed_params = []

        # <> で囲まれたLoRAパラメータを検索
        pattern = r'<lora:([^>]+)>'
        matches = re.findall(pattern, lora_text, re.IGNORECASE)
        
        # マッチした各パラメータを処理
        for match in matches:
            # print(match)
            # 空白を削除して processed_params に追加
            processed_params.append(match.strip())
        
        # lora_text から <match> を削除
        cleaned_text = re.sub(pattern, '', lora_text, flags=re.IGNORECASE)

        return processed_params, cleaned_text




"""

D2 D2 Pipe

"""
class D2_Pipe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "d2_pipe": ("D2_TD2Pipe",),
                "ckpt_name": ("STRING", {"forceInput":True},),
                "positive": ("STRING", {"forceInput":True},),
                "negative": ("STRING", {"forceInput":True},),
                "seed": ("INT", {"forceInput":True},),
                "steps": ("INT", {"forceInput":True},),
                "cfg": ("FLOAT", {"forceInput":True},),
                "sampler_name": ("STRING", {"forceInput":True},),
                "scheduler": ("STRING", {"forceInput":True},),
                "denoise": ("FLOAT", {"forceInput":True},),
                "width": ("INT", {"forceInput":True},),
                "height": ("INT", {"forceInput":True},),
            },
        }

    RETURN_TYPES = ("D2_TD2Pipe", "STRING", "STRING", "STRING", "INT", "INT", "FLOAT", "STRING", "STRING", "FLOAT", "INT", "INT", )
    RETURN_NAMES = ("d2_pipe", "ckpt_name", "positive", "negative", "seed", "steps", "cfg", "sampler_name", "scheduler", "denoise", "width", "height", )
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, d2_pipe:Optional[D2_TD2Pipe]=None, ckpt_name = None, positive = None, negative = None, seed = None, steps = None, cfg = None, sampler_name = None, scheduler = None, denoise = None, width = None, height = None):

        # d2_pipeがNoneの場合、デフォルト値で新しいインスタンスを作成
        if d2_pipe is None:
            d2_pipe = D2_TD2Pipe()
        else:
            # d2_pipeのコピーを作成して元のインスタンスを変更しないようにする
            d2_pipe = D2_TD2Pipe(
                ckpt_name = d2_pipe.ckpt_name,
                positive = d2_pipe.positive,
                negative = d2_pipe.negative,
                seed = d2_pipe.seed,
                steps = d2_pipe.steps,
                cfg = d2_pipe.cfg,
                sampler_name = d2_pipe.sampler_name,
                scheduler = d2_pipe.scheduler,
                denoise = d2_pipe.denoise,
                width = d2_pipe.width,
                height = d2_pipe.height
            )

        # 個別のパラメータがNoneでない場合、d2_pipeの値を上書き
        if ckpt_name:
            d2_pipe.ckpt_name = ckpt_name
        if positive:
            d2_pipe.positive = positive
        if negative:
            d2_pipe.negative = negative
        if seed != None:
            d2_pipe.seed = seed
        if steps != None:
            d2_pipe.steps = steps
        if cfg != None:
            d2_pipe.cfg = cfg
        if sampler_name:
            d2_pipe.sampler_name = sampler_name
        if scheduler:
            d2_pipe.scheduler = scheduler
        if denoise != None:
            d2_pipe.denoise = denoise
        if width != None:
            d2_pipe.width = width
        if height != None:
            d2_pipe.height = height

        return (d2_pipe, d2_pipe.ckpt_name, d2_pipe.positive, d2_pipe.negative, d2_pipe.seed, d2_pipe.steps, d2_pipe.cfg, d2_pipe.sampler_name, d2_pipe.scheduler, d2_pipe.denoise, d2_pipe.width, d2_pipe.height,)



NODE_CLASS_MAPPINGS = {
    # "D2 Preview Image": D2_PreviewImage,
    # "D2 Load Image": D2_LoadImage,
    # "D2 Folder Image Queue": D2_FolderImageQueue,
    "D2 KSampler": D2_KSampler,
    "D2 KSampler(Advanced)": D2_KSamplerAdvanced,
    "D2 Checkpoint Loader": D2_CheckpointLoader,
    "D2 Controlnet Loader": D2_ControlnetLoader,
    "D2 Load Lora": D2_LoadLora,
    # "D2 EmptyImage Alpha": D2_EmptyImageAlpha,
    # "D2 Grid Image": D2_GridImage,
    # "D2 Image Stack": D2_ImageStack,
    # "D2 Load Folder Images": D2_LoadFolderImages,
    "D2 Pipe": D2_Pipe,
}
