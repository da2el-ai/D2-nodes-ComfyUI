import os
import folder_paths

from types import SimpleNamespace
from comfy_api.latest import UI

from .modules.eagle_api import EagleAPI, send_to_eagle

"""

D2_SaveAudioEagle
Eagleに音声ファイルを保存する

"""
class D2_SaveAudioEagle:
    def __init__(self):
        self.eagle_api:EagleAPI = EagleAPI()
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "filename_prefix": ("STRING", {"default":"audoi/ComfyUI"},),
                "eagle_folder": ("STRING", {"default":""},),
                "format": (["FLAC", "MP3", "Opus"], {"default":"FLAC"},),
                "mp3_quality": (["V0", "128k", "320k"], {"default":"V0"},),
                "opus_quality": (["64k", "96k", "128k", "192k", "320k"], {"default":"128k"},),
                "memo_text": ("STRING",{"default": ""}),
                # これがないと再生UIが表示されない
                "audioUI": ("AUDIO_UI", {}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("STRING")
    RETURN_NAMES = ("filename")
    FUNCTION = "execute"
    CATEGORY = "D2/Audio"
    OUTPUT_NODE = True

    def execute(self, audio, filename_prefix="ComfyUI", eagle_folder="", format="FLAC", mp3_quality="V0", opus_quality="128k", memo_text="", audioUI="", prompt=None, extra_pnginfo=None):
        if format == "MP3":
            quality = mp3_quality
        elif format == "Opus":
            quality = opus_quality
        else:
            quality = None

        # EagleフォルダIDを取得
        folder_id = self.eagle_api.find_or_create_folder(eagle_folder)

        # UI.AudioSaveHelper.get_save_audio_uiが新しい形式のhiddenを期待しているのでオブジェクトを作成
        self.hidden = SimpleNamespace(prompt=prompt, extra_pnginfo=extra_pnginfo)

        # 音声の保存とファイル名の取得
        saved=UI.AudioSaveHelper.get_save_audio_ui(
            audio, filename_prefix=filename_prefix, cls=self, format=format, quality=quality
        )
        saved_dict = saved.as_dict()

        # 1ファイルずつEagleに保存
        for file_obj in saved_dict.get("audio",[]):
            file_path = os.path.join(self.output_dir, file_obj["subfolder"], file_obj["filename"])
            send_to_eagle(self.eagle_api, folder_id, file_path, memo_text)

        return {
            "ui": saved_dict
        }


NODE_CLASS_MAPPINGS = {
    "D2 Save Audio Eagle": D2_SaveAudioEagle,
}

