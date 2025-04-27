import { app, ComfyApp } from "../../scripts/app.js";
import { findWidgetByName } from "./modules/utils.js";


app.registerExtension({
    name: "Comfy.D2.D2_LoadImage",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Load Image") return;

        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const editorBtnWidget = findWidgetByName(this, "editor");
            editorBtnWidget.name = "Open Mask Editor";

            // マスクエディターを起動
            editorBtnWidget.callback = async () => {
                ComfyApp.copyToClipspace(this);
                ComfyApp.clipspace_return_node = this;
                ComfyApp.open_maskeditor();
            };
      
            return r;
        };
    },
});
