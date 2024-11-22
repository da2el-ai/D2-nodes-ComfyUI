import { app } from "/scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { findWidgetByName, sleep, getReadOnlyWidgetBase } from "./utils.js";


app.registerExtension({
    name: "Comfy.D2.D2_XYModelList",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 XY Model List") return;

        const getModelFiles = (type) => {
            return new Promise(async (resolve) => {
                const url = `/D2/model-list/get-list?type=${type}`;
                const response = await fetch(url);
                const data = await response.json();
                resolve(data.files);
            });
        }

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const btn = findWidgetByName(this, "get_list");
            const typeWidget = findWidgetByName(this, "model_type");
            const listWidget = findWidgetByName(this, "list");

            btn.callback = async () => {
                const modelList = await getModelFiles(typeWidget.value);
                listWidget.value = modelList.join("\n");
            };

            return r;
        };
    },

    getCustomWidgets(app) {
        return {
            D2_GET_MODEL_BTN(node, inputName, inputData, app) {
                const widget = node.addWidget("button", "get_list", 0, () => {});
                return widget;
            },
        };
    },
});
