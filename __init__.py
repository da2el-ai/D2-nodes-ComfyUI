"""
@author: da2el
@title: D2 Nodes
@description: A Collection of Handy Custom Nodes for ComfyUI
"""

import os
import server
from aiohttp import web
from comfy_api.latest import ComfyExtension, io
from .nodes.modules import util

# =============================================================================
# V3 スキーマ移行作業中
# -----------------------------------------------------------------------------
# V1 と V3 を混在したカスタムノードは ComfyUI に許可されないため、
# 公開方式を comfy_entrypoint（V3）へ全面的に切り替えている。
# get_node_list には「V3 化が済んだノード」だけを列挙する。
# 未移行ノードは import / リストともにコメントアウトしておき、
# 移行が済んだものからコメントを解除していく。
# 詳細は .claude/specs/v3-migration-strategy.md を参照。
# =============================================================================

# --- V1 公開方式（移行完了まで凍結） -----------------------------------------
# from .nodes.d2_nodes import NODE_CLASS_MAPPINGS as D2_CLASS_MAPPIGS
# from .nodes.d2_size_nodes import NODE_CLASS_MAPPINGS as D2_SIZE_CLASS_MAPPIGS
# from .nodes.d2_xy_nodes import NODE_CLASS_MAPPINGS as D2_XY_CLASS_MAPPIGS
# from .nodes.d2_refiner_nodes import NODE_CLASS_MAPPINGS as D2_REFINER_CLASS_MAPPIGS
# from .nodes.d2_merge_nodes import NODE_CLASS_MAPPINGS as D2_MERGE_CLASS_MAPPIGS
# from .nodes.d2_text_nodes import NODE_CLASS_MAPPINGS as D2_TEXT_CLASS_MAPPIGS
# from .nodes.d2_image_nodes import NODE_CLASS_MAPPINGS as D2_IMAGE_CLASS_MAPPIGS
# from .nodes.d2_audio_nodes import NODE_CLASS_MAPPINGS as D2_AUDIO_CLASS_MAPPIGS
#
# NODE_CLASS_MAPPINGS = {
#     **D2_CLASS_MAPPIGS,
#     **D2_SIZE_CLASS_MAPPIGS,
#     **D2_XY_CLASS_MAPPIGS,
#     **D2_REFINER_CLASS_MAPPIGS,
#     **D2_MERGE_CLASS_MAPPIGS,
#     **D2_TEXT_CLASS_MAPPIGS,
#     **D2_IMAGE_CLASS_MAPPIGS,
#     **D2_AUDIO_CLASS_MAPPIGS,
# }
# NODE_DISPLAY_NAME_MAPPINGS = []
# -----------------------------------------------------------------------------

# --- V3 化済みノードの import ------------------------------------------------
from .nodes.d2_text_nodes import (
    D2_PromptSanitizer,
    D2_MultiOutput,
    D2_ListToString,
    D2_FilenameTemplate,
    D2_FilenameTemplate2,
    D2_RegexSwitcher,
    D2_RegexReplace,
    D2_TokenCounter,
    D2_Prompt,
)
from .nodes.d2_nodes import (
    D2_KSampler,
    D2_KSamplerAdvanced,
    D2_CheckpointLoader,
    D2_LoadDiffusionModel,
    D2_ControlnetLoader,
    D2_LoadLora,
    D2_Pipe,
    D2_AnyDelivery,
    D2_PresetSelector,
)
from .nodes.d2_size_nodes import (
    D2_ResizeCalculator,
    D2_ImageResize,
    D2_SizeSelector,
    D2_GetImageSize,
)
from .nodes.d2_xy_nodes import (
    D2_XYPlot,
    D2_XYPlotEasy,
    D2_XYPlotEasyMini,
    D2_XYModelList,
    D2_XYPromptSR,
    D2_XYPromptSR2,
    D2_XYListToPlot,
    D2_XYStringToPlot,
    D2_XYSeed,
    D2_XYSeed2,
    D2_XYAnnotation,
    D2_XYGridImage,
    D2_XYFolderImages,
    D2_XYUploadImage,
)
from .nodes.d2_image_nodes import (
    D2_SaveImage,
    D2_SaveImageEagle,
    D2_SendFileEagle,
    D2_PreviewImage,
    D2_LoadImage,
    D2_EmptyImageAlpha,
    D2_LoadFolderImages,
    D2_MosaicFilter,
    D2_FolderImageQueue,
    D2_ImageStack,
    D2_ImageMaskStack,
    D2_CutByMask,
    D2_PasteByMask,
    D2_GridImage,
)


class D2Extension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            # A. 他モジュール依存がなく環境変化の影響を受けないもの
            D2_PromptSanitizer,
            D2_MultiOutput,
            D2_ListToString,
            D2_FilenameTemplate,
            D2_FilenameTemplate2,
            # D. Text 系残り
            D2_RegexSwitcher,
            D2_RegexReplace,
            D2_TokenCounter,
            D2_Prompt,
            # B. 重要度が高いもの（KSampler 系）
            D2_KSampler,
            D2_KSamplerAdvanced,
            # B. 重要度が高いもの（Loader 系）
            D2_CheckpointLoader,
            D2_LoadDiffusionModel,
            D2_ControlnetLoader,
            D2_LoadLora,
            # B. 重要度が高いもの（Size 系）
            D2_ResizeCalculator,
            D2_ImageResize,
            D2_SizeSelector,
            D2_GetImageSize,
            # B. 重要度が高いもの（Pipe / Delivery）
            D2_Pipe,
            D2_AnyDelivery,
            # B. 重要度が高いもの（Preset Selector）
            D2_PresetSelector,
            # B. 重要度が高いもの（Image 保存・読込）
            D2_SaveImage,
            D2_SaveImageEagle,
            D2_SendFileEagle,
            D2_PreviewImage,
            D2_LoadImage,
            # C. 環境依存（影響の小さいもの）
            D2_EmptyImageAlpha,
            D2_LoadFolderImages,
            D2_MosaicFilter,
            # C. 環境依存（JS 連動: 動的入力・キュー）
            D2_FolderImageQueue,
            D2_ImageStack,
            D2_ImageMaskStack,
            # C. 環境依存（複雑なマスク処理）
            D2_CutByMask,
            D2_PasteByMask,
            # C. グリッド画像（状態保持・ExecutionBlocker）
            D2_GridImage,
            # C. XY Plot コア
            D2_XYPlot,
            D2_XYPlotEasy,
            D2_XYPlotEasyMini,
            # C. XY Plot テキスト系
            D2_XYModelList,
            D2_XYPromptSR,
            D2_XYPromptSR2,
            D2_XYListToPlot,
            D2_XYStringToPlot,
            D2_XYSeed,
            D2_XYSeed2,
            D2_XYAnnotation,
            D2_XYGridImage,
            D2_XYFolderImages,
            D2_XYUploadImage,
        ]


async def comfy_entrypoint() -> ComfyExtension:
    return D2Extension()


WEB_DIRECTORY = "./web"
__all__ = ["WEB_DIRECTORY", "comfy_entrypoint"]


# css読み取り用のパスを設定
if os.path.exists(util.D2_WEB_PATH):
    server.PromptServer.instance.app.add_routes([
        web.static("/D2/assets/", str(util.D2_WEB_PATH))
    ])
