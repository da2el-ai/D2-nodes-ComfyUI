import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyWidgets } from "/scripts/widgets.js";
import { findWidgetByName } from "./modules/utils.js";

const MAX_SEED = 2 ** 32 - 1; // 4,294,967,295


app.registerExtension({
    name: "Comfy.D2.D2_MultiOutput",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Multi Output") return;

        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const typeWidget = findWidgetByName(this, "type");
            const inputWidget = findWidgetByName(this, "parameter");
            const btnWidget = findWidgetByName(this, "create_seed");
            
            btnWidget.name = "Add Random";
            btnWidget.callback = () => {
                const seed = Math.floor(Math.random() * MAX_SEED);
                inputWidget.value += inputWidget.value.length >= 1 ? "\n" : "";
                inputWidget.value += seed;
            };

            // seed生成ボタンの表示切り替え
            const changeBtnVisible = (value) => {
                if (value === "SEED") {
                    btnWidget.type = "button";
                } else {
                    btnWidget.type = "converted-widget";
                }
            };

            // seed生成ボタンの表示切り替え
            typeWidget.callback = (value) => {
                changeBtnVisible(value);
            };

            setTimeout(() => {
                changeBtnVisible(typeWidget.value);
            }, 200);
            return r;
        };
    },
});
