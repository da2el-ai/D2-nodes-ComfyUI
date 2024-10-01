import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyWidgets } from "/scripts/widgets.js";

const BUTTON_NAME = "Add Random";
const MAX_SEED = 2 ** 32 - 1; // 4,294,967,295

class D2_MultiOutputClass {
    btnWidget = undefined;
    typeWidget = undefined;
    inputWidget = undefined;

    // seed生成ボタンの表示切り替え
    changeBtnVisible(value) {
        if (value === "SEED") {
            this.btnWidget.type = "button";
        } else {
            this.btnWidget.type = "converted-widget";
        }
    }
}

const d2mo = new D2_MultiOutputClass();

app.registerExtension({
    name: "Comfy.D2.D2_MultiOutput",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Multi Output") return;

        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            d2mo.btnWidget = this.widgets?.find((w) => w.name === BUTTON_NAME);
            d2mo.typeWidget = this.widgets?.find((w) => w.name === "type");
            d2mo.inputWidget = this.widgets?.find((w) => w.name === "parameter");

            // seed生成ボタンの表示切り替え
            if (d2mo.typeWidget !== undefined) {
                d2mo.typeWidget.callback = (value) => {
                    d2mo.changeBtnVisible(value);
                };

                setTimeout(() => {
                    d2mo.changeBtnVisible(d2mo.typeWidget.value);
                }, 200);
            }

            // const r = origOnNodeCreated
            //     ? origOnNodeCreated.apply(this)
            //     : undefined;
            // for (const w of this.widgets) {
            //     if (w.name === "seed") {
            //         w.type = "converted-widget";
            //         if (!w.linkedWidgets) continue;
            //         for (const lw of w.linkedWidgets) {
            //             lw.type = "converted-widget";
            //         }
            //     }
            // }
            return r;
        };
    },
    getCustomWidgets(app) {
        return {
            D2RESET(node, inputName, inputData, app) {
                const widget = node.addWidget("button", BUTTON_NAME, 0, () => {
                    console.log("click reset");
                    const seed = Math.floor(Math.random() * MAX_SEED);
                    d2mo.inputWidget.value += d2mo.inputWidget.value.length >= 1 ? "\n" : "";
                    d2mo.inputWidget.value += seed;
                });
                return widget;
            },
        };
    },
});
