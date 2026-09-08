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
# ノードの登録について
# -----------------------------------------------------------------------------
# 登録元は各 nodes/d2_*.py 末尾の NODE_CLASS_MAPPINGS ただ一つ。
# このファイルはそれを束ねて get_node_list() に渡すだけなので、
# 【ノードを追加するときは nodes/d2_*.py の NODE_CLASS_MAPPINGS に登録すれば足りる】。
# このファイルを編集するのは「ノード定義ファイルを新規作成したとき」だけ。
#
# ComfyUI は V1（NODE_CLASS_MAPPINGS を公開する方式）と V3（comfy_entrypoint 方式）の
# 混在を許可しないため、公開は comfy_entrypoint に一本化している。
# ノード名は各ノードの Schema の node_id が使われるので、
# NODE_CLASS_MAPPINGS のキー文字列は ComfyUI からは参照されない（可読性のために揃えておく）。
# =============================================================================

from .nodes.d2_nodes import NODE_CLASS_MAPPINGS as D2_CLASS_MAPPINGS
from .nodes.d2_size_nodes import NODE_CLASS_MAPPINGS as D2_SIZE_CLASS_MAPPINGS
from .nodes.d2_xy_nodes import NODE_CLASS_MAPPINGS as D2_XY_CLASS_MAPPINGS
from .nodes.d2_refiner_nodes import NODE_CLASS_MAPPINGS as D2_REFINER_CLASS_MAPPINGS
from .nodes.d2_merge_nodes import NODE_CLASS_MAPPINGS as D2_MERGE_CLASS_MAPPINGS
from .nodes.d2_text_nodes import NODE_CLASS_MAPPINGS as D2_TEXT_CLASS_MAPPINGS
from .nodes.d2_image_nodes import NODE_CLASS_MAPPINGS as D2_IMAGE_CLASS_MAPPINGS
from .nodes.d2_audio_nodes import NODE_CLASS_MAPPINGS as D2_AUDIO_CLASS_MAPPINGS

D2_NODE_MAPPINGS = {
    **D2_CLASS_MAPPINGS,
    **D2_SIZE_CLASS_MAPPINGS,
    **D2_XY_CLASS_MAPPINGS,
    **D2_REFINER_CLASS_MAPPINGS,
    **D2_MERGE_CLASS_MAPPINGS,
    **D2_TEXT_CLASS_MAPPINGS,
    **D2_IMAGE_CLASS_MAPPINGS,
    **D2_AUDIO_CLASS_MAPPINGS,
}


class D2Extension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return list(D2_NODE_MAPPINGS.values())


async def comfy_entrypoint() -> ComfyExtension:
    return D2Extension()


WEB_DIRECTORY = "./web"
__all__ = ["WEB_DIRECTORY", "comfy_entrypoint"]


# css読み取り用のパスを設定
if os.path.exists(util.D2_WEB_PATH):
    server.PromptServer.instance.app.add_routes([
        web.static("/D2/assets/", str(util.D2_WEB_PATH))
    ])
