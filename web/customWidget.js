/**
 * 汎用カスタムウィジェット
 */
import { app } from "/scripts/app.js";
import { getReadOnlyWidgetBase, customWidgetDrawText, formatTime } from "./modules/utils.js";
import { RemainingTimeController } from "./modules/RemainingTimeController.js";

app.registerExtension({
    name: "Comfy.D2.customWidget",

    getCustomWidgets(app) {
        return {
            /**
             * 汎用ボタン
             */
            D2_BUTTON(node, inputName, inputData, app) {
                const widget = node.addWidget("button", inputName, 0, () => {});
                return widget;
            },
            
            /**
             * 汎用テキストウィジェット
             */
            D2_SIMPLE_TEXT(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase( node, "D2_SIMPLE_TEXT", inputName, "");

                widget.textTemplate = "<%value%>";
                widget.draw = function (ctx, node, width, y) {
                    const text = widget.textTemplate.replace("<%value%>", this.value);
                    customWidgetDrawText(ctx, y, text);
                };
                
                node.addCustomWidget(widget);
                // return widget;
            },
            
            /**
             * プログレスバー
             */
            D2_PROGRESS_BAR(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase(node, "D2_PROGRESS_BAR", inputName, 0);

                widget.draw = function (ctx, node, width, y) {
                    ctx.fillStyle = "#007f13";
                    ctx.fillRect(0, 0, width * this.value, 5);
                };
                node.addCustomWidget(widget);
                // return widget;
            },

            /**
             * 毎回処理を行うための表示専用seed
             */
            D2_SEED(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase(node, "D2_SEED", inputName, 0);

                // seed更新
                widget.updateSeed = () => {
                    widget.setValue(Math.floor(Math.random()*100000));
                };

                widget.draw = function (ctx, node, width, y) {
                    customWidgetDrawText(ctx, y, `Seed: ${this.value}`);
                };
                node.addCustomWidget(widget);
                // return widget;
            },

            /**
             * 残り時間表示
             * value にミリ秒を渡すと hh:mm:ss で出力する
             */
            D2_TIME(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase( node, "D2_TIME", inputName, 0);

                widget.draw = function (ctx, node, width, y) {
                    const timeStr = formatTime(this.value);
                    customWidgetDrawText(ctx, y, `Remaining Time: ${timeStr}`);
                };
                node.addCustomWidget(widget);
                // return widget;
            },
        };
    },
});
