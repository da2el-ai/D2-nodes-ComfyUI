import { app } from "/scripts/app.js";
import { sleep, findWidgetByName, getReadOnlyWidgetBase } from "./modules/utils.js";

const resetImageCount = (id) => {
  return new Promise(async (resolve) => {
    const url = `D2/grid_image/reset_image_count?id=${id}`;
    const response = await fetch(url);
    const data = await response.json();
    resolve(data.image_count);
  });
};


app.registerExtension({
  name: "Comfy.D2.D2_GridImage",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 Grid Image") return;

    /**
     * ノード実行時
     * 画像のストック数を更新
     */
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = async function (message) {
      onExecuted?.apply(this, arguments);

      const imageCount = message["image_count"][0];
      const triggerCountWidget = findWidgetByName(this, "trigger_count");
      const countWidget = findWidgetByName(this, "count");
      countWidget.setValue((parseInt(countWidget.value) + 1) % triggerCountWidget.value);
    };

  },

  getCustomWidgets(app) {
    return {
      /**
       * リセットボタン
       */
      D2_GRID_RESET(node, inputName, inputData, app) {
        
        const widget = node.addWidget("button", "Reset Images", "", async () => {
          const image_count = await resetImageCount(node.id);
          const indexWidget = findWidgetByName(node, "count");
          indexWidget.setValue(image_count);
        });
        // node.addCustomWidget(widget);
        return widget;
      },
      D2_GRID_COUNT(node, inputName, inputData, app) {
        const widget = getReadOnlyWidgetBase(node, "D2_GRID_COUNT", inputName, 0);

        widget.draw = function(ctx, node, width, y) {
          const text = `Image count: ${this.value}`;
          ctx.fillStyle = "#ffffff";
          ctx.font = "12px Arial";
          ctx.fillText(text, 20, y + 20);
        };
        node.addCustomWidget(widget);
        // return widget;
      },
    };
  },

});
