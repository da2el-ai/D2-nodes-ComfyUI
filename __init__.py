"""
@author: da2el
@title: D2 Nodes
@description: A Collection of Handy Custom Nodes for ComfyUI
"""

import os
import server
from aiohttp import web

from .nodes.d2_nodes import NODE_CLASS_MAPPINGS as D2_CLASS_MAPPIGS 
from .nodes.d2_size_nodes import NODE_CLASS_MAPPINGS as D2_SIZE_CLASS_MAPPIGS 
from .nodes.d2_xy_nodes import NODE_CLASS_MAPPINGS as D2_XY_CLASS_MAPPIGS 
from .nodes.d2_refiner_nodes import NODE_CLASS_MAPPINGS as D2_REFINER_CLASS_MAPPIGS 

WEB_DIRECTORY = "./web"
NODE_CLASS_MAPPINGS = {**D2_CLASS_MAPPIGS, **D2_SIZE_CLASS_MAPPIGS, **D2_XY_CLASS_MAPPIGS, **D2_REFINER_CLASS_MAPPIGS}
NODE_DISPLAY_NAME_MAPPINGS = []

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]


# css読み取り用のパスを設定
d2_nodes_path = os.path.join(os.path.dirname(__file__))
d2_web_path = os.path.join(d2_nodes_path, "web")

if os.path.exists(d2_web_path):
    server.PromptServer.instance.app.add_routes([
        web.static("/D2/assets/", d2_web_path)
    ])

