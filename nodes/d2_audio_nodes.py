import os
import folder_paths

from comfy_api.latest import UI, io

from .modules.eagle_api import EagleAPI, send_to_eagle

"""

D2_SaveAudioEagle
Eagleに音声ファイルを保存する

"""
class D2_SaveAudioEagle(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Save Audio Eagle",
            display_name="D2 Save Audio Eagle",
            category="D2/Audio",
            is_output_node=True,
            inputs=[
                io.Audio.Input("audio"),
                io.String.Input("filename_prefix", default="audoi/ComfyUI"),
                io.String.Input("eagle_folder", default=""),
                io.Combo.Input("format", options=["FLAC", "MP3", "Opus"], default="FLAC"),
                io.Combo.Input("mp3_quality", options=["V0", "128k", "320k"], default="V0"),
                io.Combo.Input("opus_quality", options=["64k", "96k", "128k", "192k", "320k"], default="128k"),
                io.String.Input("memo_text", default=""),
                # これがないと再生UIが表示されない
                io.Custom("AUDIO_UI").Input("audioUI"),
            ],
            # V1 は RETURN_TYPES=("STRING")（カンマ無し＝文字列）で実体は result を返さない
            # 出力ノードだったので、出力なし（ui のみ）として移行する
            outputs=[],
            hidden=[io.Hidden.prompt, io.Hidden.extra_pnginfo],
        )

    @classmethod
    def execute(cls, audio, filename_prefix="ComfyUI", eagle_folder="", format="FLAC", mp3_quality="V0", opus_quality="128k", memo_text="", audioUI=None) -> io.NodeOutput:
        if format == "MP3":
            quality = mp3_quality
        elif format == "Opus":
            quality = opus_quality
        else:
            quality = None

        eagle_api = EagleAPI()
        output_dir = folder_paths.get_output_directory()

        # EagleフォルダIDを取得
        folder_id = eagle_api.find_or_create_folder(eagle_folder)

        # AudioSaveHelper.save_audio は cls.hidden.prompt / extra_pnginfo を読むので、
        # V3 では cls をそのまま渡せばよい（V1 の SimpleNamespace 細工は不要）
        saved = UI.AudioSaveHelper.get_save_audio_ui(
            audio, filename_prefix=filename_prefix, cls=cls, format=format, quality=quality
        )
        saved_dict = saved.as_dict()

        # 1ファイルずつEagleに保存
        for file_obj in saved_dict.get("audio", []):
            file_path = os.path.join(output_dir, file_obj["subfolder"], file_obj["filename"])
            send_to_eagle(eagle_api, folder_id, file_path, memo_text)

        return io.NodeOutput(ui=saved_dict)


NODE_CLASS_MAPPINGS = {
    "D2 Save Audio Eagle": D2_SaveAudioEagle,
}

