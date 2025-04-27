/**
 * 汎用カスタムウィジェット
 */
import { app } from "/scripts/app.js";
import { getReadOnlyWidgetBase, customWidgetDrawText } from "./modules/utils.js";
import { RemainingTimeController } from "./modules/RemainingTimeController.js";

app.registerExtension({
    name: "Comfy.D2.customWidget",

    getCustomWidgets(app) {
        return {
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

                widget.draw = function (ctx, node, width, y) {
                    customWidgetDrawText(ctx, y, `Seed: ${this.value}`);
                };
                node.addCustomWidget(widget);
                // return widget;
            },

            /**
             * 残り時間表示
             */
            D2_REMAINING_TIME(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase( node, "D2_REMAINING_TIME", inputName, RemainingTimeController.INIT_TIME);

                widget.draw = function (ctx, node, width, y) {
                    customWidgetDrawText(ctx, y, `Remaining Time: ${this.value}`);
                };
                node.addCustomWidget(widget);
                // return widget;
            },
        };
    },
});
