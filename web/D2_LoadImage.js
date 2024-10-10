import { app, ComfyApp } from "../../scripts/app.js";
// import { api } from "../../scripts/api.js";
// import { ComfyWidgets } from "/scripts/widgets.js";

const BUTTON_NAME = "Open Mask Editor";

app.registerExtension({
    name: "Comfy.D2.D2_LoadImage",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Load Image") return;

        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;
            return r;
        };
    },
    getCustomWidgets(app) {
        return {
            D2MASKEDITOR(node, inputName, inputData, app) {
                const widget = node.addWidget("button", BUTTON_NAME, 0, () => {
                    ComfyApp.copyToClipspace(node);
                    ComfyApp.clipspace_return_node = node;
                    ComfyApp.open_maskeditor();
                });
                return widget;
            },
        };
    },
});
