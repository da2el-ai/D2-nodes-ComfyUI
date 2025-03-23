import { app } from "/scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { findWidgetByName, sleep, getReadOnlyWidgetBase } from "./utils.js";


app.registerExtension({
    name: "Comfy.D2.D2_XYModelList",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 XY Model List") return;

        const getModelFiles = (type, filter, mode, sortBy, orderBy) => {
            return new Promise(async (resolve) => {
                const url = `/D2/model-list/get-list?type=${type}&filter=${filter}&mode=${mode}&sort_by=${sortBy}&order_by=${orderBy}`;
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
            const filterWidget = findWidgetByName(this, "filter");
            const modeWidget = findWidgetByName(this, "mode");
            const sortByWidget = findWidgetByName(this, "sort_by");
            const orderByWidget = findWidgetByName(this, "order_by");
            const modelListWidget = findWidgetByName(this, "model_list");

            btn.callback = async () => {
                const modelList = await getModelFiles(
                    typeWidget.value, 
                    filterWidget.value,
                    modeWidget.value,
                    sortByWidget.value,
                    orderByWidget.value
                );
                modelListWidget.value = modelList.join("\n");
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
