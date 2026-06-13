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
)
from .nodes.d2_nodes import (
    D2_CheckpointLoader,
    D2_LoadDiffusionModel,
    D2_ControlnetLoader,
    D2_LoadLora,
)
from .nodes.d2_size_nodes import (
    D2_ResizeCalculator,
    D2_ImageResize,
    D2_SizeSelector,
    D2_GetImageSize,
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
