import { app } from "/scripts/app.js";
import { sleep, findWidgetByName, getReadOnlyWidgetBase, customWidgetDrawText } from "./modules/utils.js";
import { RemainingTimeController } from "./modules/RemainingTimeController.js";

app.registerExtension({
    name: "Comfy.D2.D2_XY_Plot",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (
            nodeData.name !== "D2 XY Plot" &&
            nodeData.name !== "D2 XY Plot Easy" &&
            nodeData.name !== "D2 XY Plot Easy Mini"
        )
            return;

        /**
         * ノード作成
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            // 残り時間表示ウィジェットとコントローラー
            const remTimeWidget = findWidgetByName(this, "remaining_time");
            this.d2_remTimeController = new RemainingTimeController(remTimeWidget);

            return r;
        };

        /**
         * ノード実行時
         */
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = async function (message) {
            onExecuted?.apply(this, arguments);

            const autoQueue = message["auto_queue"][0];
            const xArray = message["x_array"][0];
            const yArray = message["y_array"][0];
            const index = message["index"][0]; // 0スタート
            const total = message["total"][0];
            this.total = total;
            const indexWidget = findWidgetByName(this, "index");
            const progressBarWidget = findWidgetByName(this, "progress_bar");

            // 残り時間計算
            this.d2_remTimeController.calculateRemainingTime(index, total);

            // seed更新
            const seedWidget = findWidgetByName(this, "xy_seed");
            seedWidget.setValue(Math.floor(Math.random() * 100000));

            // まだ残りがあるならキューを入れる
            if (index + 1 < total && total >= 2) {
                indexWidget.setValue(index + 1);
                progressBarWidget.setValue((index + 1) / total);

                if (autoQueue) {
                    await sleep(200);
                    app.queuePrompt(0, 1);
                }
            }
            // 最後までいった
            else if (index + 1 >= total) {
                indexWidget.setValue(0);
                progressBarWidget.setValue(0);
            }
        };
    },

    getCustomWidgets(app) {
        return {
            D2_XYPLOT_RESET(node, inputName, inputData, app) {
                const widget = node.addWidget("button", "Set start index", "", () => {
                    const startIndexWidget = findWidgetByName(node, "start_index");
                    const indexWidget = findWidgetByName(node, "index");
                    indexWidget.setValue(startIndexWidget.value);
                });
                // node.addCustomWidget(widget);
                // return widget;
            },

            D2_XYPLOT_INDEX(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase(node, "D2_XYPLOT_INDEX", inputName, 0);
                node.total = 0;

                widget.draw = function (ctx, node, width, y) {
                    customWidgetDrawText(ctx, y, `Index: ${this.value} / ${node.total}`);
                };
                node.addCustomWidget(widget);
                // return widget;
            },
        };
    },
});
