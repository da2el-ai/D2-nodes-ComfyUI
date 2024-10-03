import torch
import math
import os
import json
import hashlib
import folder_paths
import comfy.sd
import re
import random

import comfy.samplers

from nodes import common_ksampler, CLIPTextEncode, PreviewImage

from .modules import util
from .modules import checkpoint_util


MAX_SEED = 2**32 - 1  # 4,294,967,295


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
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("IMAGE", "LATENT", "STRING", "STRING", )
    RETURN_NAMES = ("IMAGE", "LATENT", "positive", "negative",)
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"


    def run(self, model, clip, vae, seed, steps, cfg, sampler_name, scheduler, latent_image, denoise, 
            preview_method, positive, negative, prompt=None, extra_pnginfo=None, my_unique_id=None,
            add_noise=None, start_at_step=None, end_at_step=None, return_with_leftover_noise=None, sampler_type="regular"):

        print("Normal -----------------")
        print(positive)

        util.set_preview_method(preview_method)

        (positive_encoded,) = CLIPTextEncode().encode(clip, positive)
        (negative_encoded,) = CLIPTextEncode().encode(clip, negative)

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
            "result": (samp_images, latent, positive, negative,)
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
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "my_unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("IMAGE", "LATENT", "STRING", "STRING", )
    RETURN_NAMES = ("IMAGE", "LATENT", "positive", "negative",)
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, model, clip, vae, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, latent_image, 
            start_at_step, end_at_step, return_with_leftover_noise,
            preview_method, positive, negative, prompt=None, extra_pnginfo=None, my_unique_id=None, denoise=1.0):

        print("Advanced -----------------")
        print(positive)

        return super().run(model, clip, vae, noise_seed, steps, cfg, sampler_name, scheduler, latent_image, denoise,
            preview_method, positive, negative, prompt, extra_pnginfo, my_unique_id,
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
            },
            "hidden": {
                "unique_id": "UNIQUE_ID", "extra_pnginfo": "EXTRA_PNGINFO", "prompt": "PROMPT"}
            }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "vae", "ckpt_name", "ckpt_hash", "ckpt_fullpath")
    FUNCTION = "load_checkpoint"

    CATEGORY = "D2"

    def load_checkpoint(self, ckpt_name, output_vae=True, output_clip=True, unique_id=None, extra_pnginfo=None, prompt=None):
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        hash = checkpoint_util.get_file_hash(ckpt_path)
        ckpt_name = os.path.basename(ckpt_name)
        return out[:3] + (ckpt_name, hash, ckpt_path)



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
            },
            "optional": {
                # 先頭に結合するテキスト
                "prefix": (
                    "STRING", {"forceInput": True, "multiline": True, "default":"",},
                ),
                # 最後に結合するテキスト
                "suffix": (
                    "STRING", {"forceInput": True, "multiline": True, "default":"",},
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT",)
    RETURN_NAMES = ("combined_text", "prefix", "suffix", "index",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, text, regex_and_output, prefix="", suffix=""):
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
        combined_text = f"{prefix}{match_text}{suffix}"

        return {
            "ui": {"text": text}, 
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

D2 PromptSR
入力された文字列を書き換えて LIST 出力するノード
qq-nodes-comfyui の XY Plot で使用

"""
class D2_PromptSR:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # プロンプト
                "prompt": (
                    "STRING", {"multiline": True},
                ),
                # 検索ワード
                "search_txt": (
                    "STRING", {"multiline": False},
                ),
                # 置換文字列
                "replace": (
                    "STRING", {"multiline": True},
                ),
            },
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("LIST",)
    FUNCTION = "replace_text"
    CATEGORY = "D2"

    def replace_text(self, prompt, search_txt, replace):
        # 置換文字列を改行で分割
        replace_options = replace.strip().split('\n')

        # 出力リスト
        output_list = [prompt]

        # 文字列を検索して置換
        for option in replace_options:
            new_prompt = prompt.replace(search_txt, option)
            output_list.append(new_prompt)

        return (output_list,)



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

D2 SizeSelector
画像サイズセレクター
指定サイズの latent も取得できる

"""
class D2_SizeSelector:

    @classmethod
    def INPUT_TYPES(cls):
        # 設定を読む
        config_path = util.get_config_path("sizeselector_config.yaml")
        config_sample_path = util.get_config_path("sizeselector_config.sample.yaml")
        config_value = util.load_config(config_path, config_sample_path)

        cls.size_dict = config_value["size_dict"]
        cls.size_list = ["custom"]
        cls.size_list.extend(cls.size_dict.keys())

        return {
            "required": {
                "preset": (cls.size_list,),
                "width": ("INT", {"default": 1024, "min": 64, "max": 8192}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 8192}),
                "swap_dimensions": (["Off", "On"],),
                "upscale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 100.0, "step":0.1}),
                "prescale_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 100.0, "step":0.1}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64})
            }
        }

    RETURN_TYPES = ("INT", "INT", "FLOAT", "FLOAT", "INT", "LATENT",)
    RETURN_NAMES = ("width", "height", "upscale_factor", "prescale_factor", "batch_size", "empty_latent",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, preset, width, height, swap_dimensions, upscale_factor, prescale_factor, batch_size):

        if(preset != "custom"):
            width = self.__class__.size_dict.get(preset).get("width", width)
            height = self.__class__.size_dict.get(preset).get("height", height)

        if swap_dimensions == "On":
            width, height = height, width

        width = int(width*prescale_factor)
        height = int(height*prescale_factor)

        latent = torch.zeros([batch_size, 4, height // 8, width // 8])

        return(width, height, upscale_factor, prescale_factor, batch_size, {"samples":latent}, )



"""

D2_RefinerSteps
Refinerの切り替えステップをステップ数で指定する

"""
class D2_RefinerSteps:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {"default": 25, "min":0}),
                "start": ("INT", {"default": 0, "min":0}),
                "end": ("INT", {"default": 5, "min":0}),
            }
        }
    RETURN_TYPES = ("INT", "INT", "INT", "INT",)
    RETURN_NAMES = ("steps", "start", "end", "refiner_start",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, steps, start, end):
        refiner_start = end + 1
        return(steps, start, end, refiner_start,)



"""

D2 Refiner Steps A1111
Refinerの切り替えステップを％で指定する

"""
class D2_RefinerStepsA1111:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {"default": 25}),
                "denoise": ("FLOAT", {"default": 1, "min":0, "max":1, "step":0.01}),
                "switch_at": ("FLOAT", {"default": 0.2, "min":0, "max":1, "step":0.01}),
            }
        }
    RETURN_TYPES = ("INT", "INT", "INT", "INT",)
    RETURN_NAMES = ("steps", "start", "end", "refiner_start",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, steps, denoise, switch_at):
        real_steps = math.floor(steps / denoise)
        start = real_steps - steps
        end = math.floor((real_steps - start) * switch_at) + start
        refiner_start = end + 1

        return(real_steps, start, end, refiner_start,)




"""

D2 Refiner Steps Tester
Refiner Steps の計算結果を確認するノード

"""
class D2_RefinerStepsTester:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {"forceInput":True}),
            },
            "optional": {
                "start": ("INT", {"forceInput":True}),
                "end": ("INT", {"forceInput":True}),
                "refiner_start": ("INT", {"forceInput":True}),
            }
        }

    # INPUT_IS_LIST = True
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, steps=0, start=0, end=0, refiner_start=0):
        text = f"stesps: {steps}\nstart: {start}\nend: {end}\nrefiner_start: {refiner_start}"
        return {"ui": {"text": text}, "result": (text,)}




NODE_CLASS_MAPPINGS = {
    "D2 KSampler": D2_KSampler,
        "D2 KSampler(Advanced)": D2_KSamplerAdvanced,
    "D2 Checkpoint Loader": D2_CheckpointLoader,
    "D2 Regex Switcher": D2_RegexSwitcher,
    "D2 Prompt SR": D2_PromptSR,
    "D2 Multi Output": D2_MultiOutput,
    "D2 Size Slector": D2_SizeSelector,
    "D2 Refiner Steps": D2_RefinerSteps,
    "D2 Refiner Steps A1111": D2_RefinerStepsA1111,
    "D2 Refiner Steps Tester": D2_RefinerStepsTester,
}


