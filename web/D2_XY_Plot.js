import { app } from "/scripts/app.js";
import { sleep, findWidgetByName, getReadOnlyWidgetBase } from "./utils.js";

app.registerExtension({
  name: "Comfy.D2.D2_XY_Plot",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 XY Plot" && nodeData.name !== "D2 XY Plot Easy") return;

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
      
      // seed更新
      const seedWidget = findWidgetByName(this, "xy_seed");
      if(seedWidget){
        seedWidget.setValue(Math.floor(Math.random()*100000));
      }

      // まだ残りがあるならキューを入れる
      if(index + 1 < total && total >= 2){
        indexWidget.setValue(index + 1);

        if(autoQueue){
          await sleep(200);
          app.queuePrompt(0, 1);
        }
      }
      // 最後までいった
      else if(index + 1 >= total){
        indexWidget.setValue(0);
      }
    };

  },

  getCustomWidgets(app) {
    return {
      D2_XYPLOT_RESET(node, inputName, inputData, app) {
        const widget = node.addWidget("button", "Reset index", "", () => {
          const indexWidget = findWidgetByName(node, "index");
          indexWidget.setValue(0);
        });
        node.addCustomWidget(widget);
        return widget;
      },
      D2_XYPLOT_INDEX(node, inputName, inputData, app) {
        const widget = getReadOnlyWidgetBase(node, "D2_XYPLOT_INDEX", inputName, 0);
        node.total = 0;

        widget.draw = function(ctx, node, width, y) {
          const text = `Index: ${this.value} / ${node.total}`;
          ctx.fillStyle = "#ffffff";
          ctx.font = "12px Arial";
          ctx.fillText(text, 20, y + 20);
        };
        node.addCustomWidget(widget);
        return widget;
      },
      D2_XYPLOT_SEED(node, inputName, inputData, app) {
        const widget = getReadOnlyWidgetBase(node, "D2_XYPLOT_SEED", inputName, 0);

        widget.draw = function(ctx, node, width, y) {
          const text = `Seed: ${this.value}`;
          ctx.fillStyle = "#ffffff";
          ctx.font = "12px Arial";
          ctx.fillText(text, 20, y + 20);
        };
        node.addCustomWidget(widget);
        return widget;
      },
    };
  },

});
