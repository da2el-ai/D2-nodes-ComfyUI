# from typing import Optional
# import torch
import os
import json
import re
# import random
# from PIL import Image, ImageOps, ImageSequence, ImageFile
# import numpy as np
from aiohttp import web
# from torchvision import transforms
# import numpy as np
from transformers import CLIPTokenizer
from datetime import datetime

import folder_paths
# import comfy.sd
# import comfy.samplers
# from comfy_extras.nodes_model_advanced import RescaleCFG, ModelSamplingDiscrete

# from comfy_execution.graph_utils import GraphBuilder
# from comfy_execution.graph import ExecutionBlocker
# from nodes import common_ksampler, CLIPTextEncode, PreviewImage, LoadImage, SaveImage, ControlNetApplyAdvanced, LoraLoader
from server import PromptServer
# from nodes import NODE_CLASS_MAPPINGS as nodes_NODE_CLASS_MAPPINGS

from .modules import util
from .modules.util import D2_TD2Pipe, AnyType, delete_comment
# from .modules import checkpoint_util
# from .modules import pnginfo_util
# from .modules import grid_image_util
from .modules.template_util import replace_template



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
        
        parts = [p.strip("\n\t") for p in regex_replace.split('--')]
        pairs = []

        for i in range(0, len(parts), 2):
            search = parts[i]
            if search:  # 検索文字があれば
                replace = parts[i + 1] if i + 1 < len(parts) else ""
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

    RETURN_TYPES = ("LIST", "STRING",)
    RETURN_NAMES = ("LIST", "x / y_list",)
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

        return (output_list, parameter,)




"""

TokenCounter
トークン化と計数を行うユーティリティクラス

"""
class TokenCounter:
    def __init__(self):
        # 明示的に初期化
        self.tokenizer = None
        self.loaded_tokenizer_name = None
    
    def load_tokenizer(self, clip_name):
        """正しいCLIPトークナイザーを読み込む"""
        if clip_name == "ViT-L/14":
            tokenizer_name = "openai/clip-vit-large-patch14"
        elif clip_name == "ViT-B/32":
            tokenizer_name = "openai/clip-vit-base-patch32"
        elif clip_name == "ViT-B/16":
            tokenizer_name = "openai/clip-vit-base-patch16"
        else:
            raise ValueError(f"Unknown CLIP model: {clip_name}")
        
        # 新しいトークナイザーが必要な場合のみロードする
        if self.tokenizer is None or self.loaded_tokenizer_name != tokenizer_name:
            try:
                self.tokenizer = CLIPTokenizer.from_pretrained(tokenizer_name)
                self.loaded_tokenizer_name = tokenizer_name
                # print(f"Loaded CLIP tokenizer: {tokenizer_name}")
            except Exception as e:
                print(f"Error loading tokenizer {tokenizer_name}: {e}")
                # フォールバックとしてデフォルトのCLIPトークナイザーを試す
                self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
                self.loaded_tokenizer_name = "openai/clip-vit-large-patch14"
                print("Loaded fallback tokenizer: openai/clip-vit-large-patch14")
        
        # トークナイザーが正しくロードされたことを確認
        if self.tokenizer is None:
            raise ValueError("Failed to load tokenizer")
    
    def count_tokens(self, text, clip_name="ViT-L/14"):
        """
        テキストをトークン化して、トークン数とトークン化された結果を返す
        """
        # トークナイザーをロード
        self.load_tokenizer(clip_name)
        
        # トークナイザーが正しくロードされていることを確認
        if self.tokenizer is None:
            raise ValueError("Tokenizer is not loaded")
        
        # テキストをトークン化
        tokens = self.tokenizer.encode(text)
        token_count = len(tokens)
        
        # トークン化の詳細結果を取得
        tokenized_words = []
        for word in text.split():
            word_tokens = self.tokenizer.encode(" " + word if word != text.split()[0] else word)
            # BPEトークナイザーの場合は先頭に特殊トークンが付くことがあるので除去
            if len(word_tokens) > 0 and word_tokens[0] == self.tokenizer.bos_token_id:
                word_tokens = word_tokens[1:]
            
            # トークンIDからテキスト表現に変換
            token_texts = [self.tokenizer.decode([t]) for t in word_tokens]
            
            tokenized_words.append({
                "word": word,
                "token_count": len(word_tokens),
                "tokens": token_texts
            })
        
        # 人間が読みやすい形式でトークン化結果を整形
        result_text = f"合計トークン数: {token_count}\n\n"
        result_text += "トークン化された単語:\n"
        for item in tokenized_words:
            result_text += f"「{item['word']}」({item['token_count']}トークン): {', '.join(item['tokens'])}\n"
        
        # 特殊トークンとその意味について説明
        result_text += "\n特殊トークン情報:\n"
        special_tokens = {
            self.tokenizer.bos_token: "文章の開始",
            self.tokenizer.eos_token: "文章の終了",
            self.tokenizer.pad_token: "パディング",
            self.tokenizer.unk_token: "未知のトークン"
        }
        for token, description in special_tokens.items():
            if token:  # Noneでないことを確認
                result_text += f"{token}: {description}\n"
        
        return (token_count, result_text)


"""

D2 TokenCounter
プロンプトのトークンを数える

"""
class D2_TokenCounter:
    
    def __init__(self):
        self.token_counter = TokenCounter()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "clip_name": (["ViT-L/14", "ViT-B/32", "ViT-B/16"], {"default": "ViT-L/14"}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("token_count", "tokenized_result")
    FUNCTION = "count_tokens"
    CATEGORY = "D2"
    
    def count_tokens(self, text, clip_name):
        """
        テキストをトークン化して、トークン数とトークン化された結果を返す
        """
        return self.token_counter.count_tokens(text, clip_name)


"""
プロンプトのトークンカウンターをAPIで用意
D2/token-counter/get-count
という形式でリクエストが届く
"""
@PromptServer.instance.routes.post("/D2/token-counter/get-count")
async def route_d2_token_counter_get_count(request):
    count = 0
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        comment_type = data.get("comment_type", "")
        new_prompt = delete_comment(prompt, comment_type)
        token_counter = TokenCounter()
        count, _ = token_counter.count_tokens(new_prompt)
    except Exception as e:
        print(f"Error in token counter API: {str(e)}")
        count = 0

    # JSON応答を返す
    json_data = json.dumps({"count": count})
    return web.Response(text=json_data, content_type='application/json')



"""

D2 Prompt
トークン計算機能とコメント削除機能がついたテキスト入力

"""
class D2_Prompt:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING",{"multiline": True},),
                "comment_type": (["# + // + /**/","# only","// only","/* */ only","None"],),
            },
            "optional": {
                "counter": ("D2_TOKEN_COUNTER", {})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "run"
    CATEGORY = "D2"

    ######
    def run(self, prompt, comment_type, counter = ""):
        new_prompt = delete_comment(prompt, comment_type)
        return (new_prompt,)



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


"""

D2 Delete Comment

"""
class D2_DeleteComment:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "","multiline": True}),
                "type": (["# only","// only","/* */ only","# + // + /**/",],),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "D2"

    def run(self, text, type):
        """
        text のコメント行を消す
        type: "# only" なら行頭が「#」の行を消す
        type: "// only" なら行頭が「//」の行を消す
        type: "/* */ only" なら「/* 〜 */」を消す。これは複数行にも対応する
        type: "# + // + /**/" なら上記3つを全て実行する
        """
        
        result_text = text
        
        if type == "# only" or type == "# + // + /**/":
            # 行頭が # のコメント行を削除（行頭の空白は考慮しない）
            result_text = re.sub(r'^#.*$', '', result_text, flags=re.MULTILINE)
        
        if type == "// only" or type == "# + // + /**/":
            # 行頭が // のコメント行を削除（行頭の空白は考慮しない）
            result_text = re.sub(r'^//.*$', '', result_text, flags=re.MULTILINE)
        
        if type == "/* */ only" or type == "# + // + /**/":
            # /* */ コメントを削除（複数行対応）
            result_text = re.sub(r'/\*.*?\*/', '', result_text, flags=re.DOTALL)
        
        # # 空行が連続する場合、1つの空行にまとめる
        # result_text = re.sub(r'\n\s*\n+', '\n\n', result_text)
        
        # # 先頭と末尾の余分な改行を削除
        # result_text = result_text.strip()

        return {
            "result": (result_text,),
        }



NODE_CLASS_MAPPINGS = {
    "D2 Regex Switcher": D2_RegexSwitcher,
    "D2 Regex Replace": D2_RegexReplace,
    "D2 Token Counter": D2_TokenCounter,
    "D2 Multi Output": D2_MultiOutput,
    "D2 List To String": D2_ListToString,
    "D2 Filename Template": D2_FilenameTemplate,
    "D2 Delete Comment": D2_DeleteComment,
    "D2 Prompt": D2_Prompt,
}
