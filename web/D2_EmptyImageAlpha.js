import { app } from "/scripts/app.js";
// import { $el } from "../../../scripts/ui.js";
import { findWidgetByName, sleep, getReadOnlyWidgetBase } from "./modules/utils.js";

class ColorSampleController {
    sampleWidget;
    redWidget;
    greenWidget;
    blueWidget;

    constructor(sampleWidget, redWidget, greenWidget, blueWidget){
        this.sampleWidget = sampleWidget;
        this.redWidget = redWidget;
        this.greenWidget = greenWidget;
        this.blueWidget = blueWidget;

        [redWidget, greenWidget, blueWidget].forEach((rgbWidget)=>{
            rgbWidget.callback = async (val) => {
                this.updateSample();
            };
        });

        // 初期値を設定
        this.updateSample();
    }

    updateSample(){
        const r = Math.floor(this.redWidget.value);
        const g = Math.floor(this.greenWidget.value);
        const b = Math.floor(this.blueWidget.value);

        const toHex = (c) => {
            const hex = c.toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        };

        const hexColor = `#${toHex(r)}${toHex(g)}${toHex(b)}`;
        this.sampleWidget.value = hexColor;
        // 再描画をトリガーするために node の setDirtyCanvas を呼ぶ
        if (this.sampleWidget.canvas) {
            this.sampleWidget.canvas.setDirty(true, true);
        }
    }
}

/////////////////////////////////////////
/////////////////////////////////////////
/////////////////////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_EmptyImageAlpha",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 EmptyImage Alpha") return;

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const sampleWidget = findWidgetByName(this, "sample");
            const redWidget = findWidgetByName(this, "red");
            const greenWidget = findWidgetByName(this, "green");
            const blueWidget = findWidgetByName(this, "blue");

            const sampleControll = new ColorSampleController(sampleWidget, redWidget, greenWidget, blueWidget);

            return r;
        };
    },

    /**
     * D2_COLOR_CANVAS サンプル色を表示
     */
    getCustomWidgets(app) {
        return {
            D2_COLOR_CANVAS(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase(node, "D2_COLOR_CANVAS", inputName, "#000000"); // 初期値を設定

                widget.draw = function (ctx, node, width, y) {
                    // 背景描画
                    ctx.fillStyle = this.value || "#000000"; // widget.value を使用
                    ctx.fillRect(20, y, width - 40, this.size[1]);
                };
                node.addCustomWidget(widget);
                return widget;
            },
        };
    },
});
