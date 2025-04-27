import { app } from "/scripts/app.js";
import { findInputByName, findWidgetByName, getReadOnlyWidgetBase } from "./modules/utils.js";

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
     * ノード作成された
     */
    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

      const indexWidget = findWidgetByName(this, "count");
      const resetBtnWidget = findWidgetByName(this, "reset");

      // ストック画像をリセット
      resetBtnWidget.callback = async () => {
        const image_count = await resetImageCount(this.id);
        indexWidget.setValue(image_count);
      };

      return r;
    };
    

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
