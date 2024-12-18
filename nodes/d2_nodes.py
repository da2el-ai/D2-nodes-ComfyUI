from typing import Optional
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
import node_helpers
import comfy.samplers
from comfy_extras.nodes_model_advanced import RescaleCFG, ModelSamplingDiscrete

from comfy_execution.graph_utils import GraphBuilder
from comfy_execution.graph import ExecutionBlocker
from nodes import common_ksampler, CLIPTextEncode, PreviewImage, LoadImage, SaveImage, ControlNetApplyAdvanced
from server import PromptServer
from nodes import NODE_CLASS_MAPPINGS as nodes_NODE_CLASS_MAPPINGS

from .modules import util
from .modules.util import D2_TXYPipe, AnyType
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

    CATEGORY = "D2"

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
    CATEGORY = "D2"

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
    CATEGORY = "D2"

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
    CATEGORY = "D2"

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
    CATEGORY = "D2"

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
                "xy_pipe": ("D2_TXYPipe",),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("IMAGE", "LATENT", "STRING", "STRING", "CONDITIONING", "CONDITIONING", )
    RETURN_NAMES = ("IMAGE", "LATENT", "positive", "negative", "positive_cond", "negative_cond", )
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"


    def run(self, model, clip, vae, seed, steps, cfg, sampler_name, scheduler, latent_image, denoise, 
            preview_method, positive, negative, positive_cond=None, negative_cond=None, cnet_stack=None, 
            xy_pipe:Optional[D2_TXYPipe]=None, prompt=None, extra_pnginfo=None, my_unique_id=None,
            add_noise=None, start_at_step=None, end_at_step=None, return_with_leftover_noise=None, sampler_type="regular"):

        util.set_preview_method(preview_method)

        # pipeがあったらそれを優先する
        if xy_pipe != None:
            positive = xy_pipe.positive if xy_pipe.positive else positive
            negative = xy_pipe.negative if xy_pipe.negative else negative
            seed = xy_pipe.seed if xy_pipe.seed else seed
            steps = xy_pipe.steps if xy_pipe.steps else steps
            cfg = xy_pipe.cfg if xy_pipe.cfg else cfg
            sampler_name = xy_pipe.sampler_name if xy_pipe.sampler_name else sampler_name
            scheduler = xy_pipe.scheduler if xy_pipe.scheduler else scheduler
            denoise = xy_pipe.denoise if xy_pipe.denoise else denoise

        # コンディショニングが入力されていたらそちらを優先する
        if positive_cond != None:
            positive_encoded = positive_cond
        else:
            (positive_encoded,) = CLIPTextEncode().encode(clip, positive)
        
        if negative_cond != None:
            negative_encoded = negative_cond
        else:
            (negative_encoded,) = CLIPTextEncode().encode(clip, negative)

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
            model, seed, steps, cfg, sampler_name, scheduler, positive_encoded, negative_encoded, latent_image, denoise=denoise, 
            disable_noise=disable_noise, start_step=start_at_step, last_step=end_at_step, force_full_denoise=force_full_denoise
        )[0]

        latent_samples = latent['samples']
        samp_images = vae.decode(latent_samples).cpu()
        results_images = PreviewImage().save_images(samp_images, "d2", prompt, extra_pnginfo)['ui']['images']

        return {
            "ui": {"images": results_images},
            "result": (samp_images, latent, positive, negative, positive_encoded, negative_encoded,)
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
                "xy_pipe": ("D2_TXYPipe",),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("IMAGE", "LATENT", "STRING", "STRING", "CONDITIONING", "CONDITIONING", )
    RETURN_NAMES = ("IMAGE", "LATENT", "positive", "negative", "positive_cond", "negative_cond", )

    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, model, clip, vae, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, latent_image, 
            start_at_step, end_at_step, return_with_leftover_noise,
            preview_method, positive, negative, positive_cond=None, negative_cond=None, cnet_stack=None, xy_pipe=None, prompt=None, extra_pnginfo=None, my_unique_id=None, denoise=1.0):

        return super().run(model, clip, vae, noise_seed, steps, cfg, sampler_name, scheduler, latent_image, denoise,
            preview_method, positive, negative, positive_cond, negative_cond, cnet_stack, xy_pipe, prompt, extra_pnginfo, my_unique_id,
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

D2 RegexSwitcher
正規表現で検索して文字列を結合・出力するノード

"""
class D2_RegexSwitcher:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 検索対象テキスト
                "text": (
                    "STRING", {"forceInput": True, "multiline": True, "default": ""},
                ),
                # 正規表現、出力テキストのペア
                "regex_and_output": (
                    "STRING", {"multiline": True, "default": "pony\n--\nscore_9,\n--\n--\nhighres, high quality,"},
                ),
                "pre_delim": (["Comma", "Line break", "None"],),
                "suf_delim": (["Comma", "Line break", "None"],),
                "show_text": (["False", "True"],),
                # 入力確認用
                "text_check": ("STRING", {"multiline": True},),
            },
            "optional": {
                # 先頭に結合するテキスト
                "prefix": ("STRING", {"forceInput": True, "multiline": True, "default":"",},),
                # 最後に結合するテキスト
                "suffix": ("STRING", {"forceInput": True, "multiline": True, "default":"",},),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT",)
    RETURN_NAMES = ("combined_text", "prefix", "suffix", "index",)
    FUNCTION = "run"
    CATEGORY = "D2"

    DELIMITER = {
        "Comma": ",",
        "Line break": "\n",
        "None": "",
    }

    def run(self, text, regex_and_output, pre_delim, suf_delim, show_text="True", prefix="", suffix="", text_check=""):
        """
        正規表現に基づいてテキストをマッチングし、結果を結合して返す関数。

        Args:
            text (str): マッチング対象のテキスト
            regex_and_output (str): 正規表現とその出力のペアを "--" で区切った文字列
            prefix (str): 結果の前に付加するテキスト
            suffix (str): 結果の後に付加するテキスト

        Returns:
            dict: UI用のテキストと結果のタプルを含む辞書
        """
        regex_output_list, default_output = D2_RegexSwitcher.get_regex_list(regex_and_output)
        match_text, match_index = D2_RegexSwitcher.get_mach_text(regex_output_list, default_output, text)

        # 文字列を結合
        parts = []
        if prefix:
            parts.append(prefix)
            parts.append(self.DELIMITER[pre_delim])
        parts.append(match_text)
        if suffix:
            parts.append(self.DELIMITER[suf_delim])
            parts.append(suffix)

        combined_text = "".join(parts)

        return {
            "ui": {"text": (text,)}, 
            "result": (combined_text, prefix, suffix, match_index)
        }

    """
    該当文字列と該当indexを取得
    """
    @staticmethod
    def get_mach_text(regex_output_list, default_output, text):
        # 各正規表現をチェックし、マッチしたら対応する出力を返す
        for index, item in enumerate(regex_output_list):
            # match_text = re.sub(item["regex"], item["output"], text, flags=re.IGNORECASE)
            # if match_text != text:
            if re.search(item["regex"], text, re.IGNORECASE):
                return item["output"], index

        # マッチしなかった場合はデフォルト出力を返す
        return default_output, -1

    """
    regex_and_output を -- で分割し、ペアにする
    """    
    @staticmethod
    def get_regex_list(text:str):
        pairs = text.split('--')
        regex_output_list = []
        default_output = None

        # ペアをリストに整理する
        for i in range(0, len(pairs), 2):
            if i + 1 < len(pairs):
                regex = pairs[i].strip()
                output = pairs[i+1].strip()
                if regex:
                    regex_output_list.append({
                        'regex': regex,
                        'output': output
                    })
                else:
                    default_output = output

        return regex_output_list, default_output



"""

D2 RegexReplace
正規表現で文字列置換

"""
class D2_RegexReplace:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": (
                    "STRING", {"forceInput": True, "multiline": True, "default": ""},
                ),
                "mode": (["Tag", "Advanced",],),
                "regex_replace": (
                    "STRING", {"multiline": True, "default": ""},
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, text, mode="Tag", regex_replace=""):
        if not text or not regex_replace:
            return { "result": (text,) }

        replace_pairs = D2_RegexReplace._parse_regex_replace(regex_replace)

        if mode == "Tag":
            result_text = D2_RegexReplace._repalace_tag(text, replace_pairs)
        else:
            result_text = D2_RegexReplace._repalace_advanced(text, replace_pairs)
        
        return {"result": (result_text,)}


    @classmethod
    def _repalace_tag(cls, result_text, replace_pairs):
        """
        result_text をカンマまたは改行で分割し、分割した要素に対して置換を行う
        置換後に空（または空白文字のみ）の要素は除外する
        """
        try:
            # カンマまたは改行で分割して、各要素をトリム
            tags = [tag.strip() for tag in re.split('[,\n]', result_text)]
            # 空の要素を削除
            tags = [tag for tag in tags if tag]
            
            # 各タグに対して正規表現による置換を適用
            new_tags = []
            for tag in tags:
                new_tag = tag
                for search_pattern, replace_pattern in replace_pairs:
                    try:
                        new_tag = re.sub(search_pattern, replace_pattern, new_tag)
                    except re.error as e:
                        return f"Regex error in tag '{tag}': {str(e)}"
                
                # 置換後のタグが空でない場合のみ追加
                if new_tag.strip():
                    new_tags.append(new_tag)
            
            # カンマ区切りで結合して返す
            return ', '.join(new_tags)
        
        except Exception as e:
            return f"Error during tag replacement: {str(e)}"
        

    @classmethod
    def _repalace_advanced(cls, result_text, replace_pairs):
        """
        result_text 全体を正規表現で置換する
        """
        for search_pattern, replace_pattern in replace_pairs:
            try:
                result_text = re.sub(search_pattern, replace_pattern, result_text, flags=re.DOTALL | re.MULTILINE)
            except re.error as e:
                return {"result": (f"Regex error: {str(e)}",)}
            except Exception as e:
                return {"result": (f"Error during replacement: {str(e)}",)}
            
        return result_text


    @classmethod
    def _parse_regex_replace(cls, regex_replace):
        """
        検索条件と置換文字のペアを作成
        """
        if not regex_replace.strip():
            return []
        
        parts = [p.strip() for p in regex_replace.split('--')]
        pairs = []

        for i in range(0, len(parts), 2):
            search = parts[i].strip()
            if search:  # 検索文字があれば
                replace = parts[i + 1].strip() if i + 1 < len(parts) else ""
                pairs.append((search, replace))
        
        return pairs



"""

D2 MultiOutput
数値、文字列、SEEDのリストを出力するノード

"""
class D2_MultiOutput:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 入力タイプ
                "type": (["FLOAT","INT","STRING","SEED",],),
                # プロンプト
                "parameter": (
                    "STRING",{"multiline": True},
                ),
            },
            "optional": {
                "reset": ("D2RESET", {})
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("LIST",)
    FUNCTION = "output_list"
    CATEGORY = "D2"

    ######
    # def output_list(self, type, parameter, seed):
    def output_list(self, type, parameter, reset = ""):

        # 入力文字列を改行で分割
        param_options = parameter.strip().split('\n')

        # 出力リスト
        output_list = []

        # 文字列を検索して置換
        for option in param_options:
            if type == "INT" or type == "SEED":
                output_list.append(int(option))
            elif type == "FLOAT":
                output_list.append(float(option))
            else:
                output_list.append(option)

        return (output_list,)




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
    CATEGORY = "D2"

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
    CATEGORY = "D2"

    def run(self, images, max_columns, grid_gap, swap_dimensions, trigger_count, count=0, reset=None, unique_id=0):
        # 画像をスタックして個数を取得
        image_count = D2_GridImage_ImageStocker.add_image(unique_id, images)

        if image_count >= trigger_count:
            grid_image = self.__class__.create_grid_image(
                max_columns = max_columns,
                image_batch = D2_GridImage_ImageStocker.get_images(unique_id), 
                grid_gap = grid_gap, 
                swap_dimensions = swap_dimensions
            )
            grid_image = util.pil2tensor(grid_image)
            D2_GridImage_ImageStocker.reset_images(unique_id)

            return {
                "result": (grid_image,),
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

D2 List To String

"""
class D2_ListToString:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "LIST": ("LIST",),
                "separator": (util.SEPARATOR,),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, LIST, separator):
        output = util.list_to_text(LIST, separator)
        return {
            "result": (output,),
        }


"""

D2 Filename Template

"""
class D2_FilenameTemplate:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format": ("STRING",{},),
            },
            "optional": {
                "arg_1": (AnyType("*"), {"forceInput": True}),
                "arg_2": (AnyType("*"), {"forceInput": True}),
                "arg_3": (AnyType("*"), {"forceInput": True}),
            },
            "hidden": {"prompt": "PROMPT"},
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, format, arg_1=None, arg_2=None, arg_3=None, prompt={}):
        text = replace_template(format, arg_1, arg_2, arg_3, prompt)
        return {
            "result": (text,),
        }




NODE_CLASS_MAPPINGS = {
    "D2 Preview Image": D2_PreviewImage,
    "D2 Load Image": D2_LoadImage,
    "D2 Folder Image Queue": D2_FolderImageQueue,
    "D2 KSampler": D2_KSampler,
    "D2 KSampler(Advanced)": D2_KSamplerAdvanced,
    "D2 Checkpoint Loader": D2_CheckpointLoader,
    "D2 Controlnet Loader": D2_ControlnetLoader,
    "D2 Regex Switcher": D2_RegexSwitcher,
    "D2 Regex Replace": D2_RegexReplace,
    "D2 EmptyImage Alpha": D2_EmptyImageAlpha,
    "D2 Multi Output": D2_MultiOutput,
    "D2 Grid Image": D2_GridImage,
    "D2 Image Stack": D2_ImageStack,
    "D2 Load Folder Images": D2_LoadFolderImages,
    "D2 List To String": D2_ListToString,
    "D2 Filename Template": D2_FilenameTemplate,
}


