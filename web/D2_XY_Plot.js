import { app } from "/scripts/app.js";
import { sleep, findWidgetOrInputsByName, findWidgetByName, findWidgetByType } from "./utils.js";

app.registerExtension({
  name: "Comfy.D2.D2_XY_Plot",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 XY Plot") return;

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
      const indexWidget = findWidgetByName(this, "index");

      // まだ残りがあるならキューを入れる
      if(index + 1 < total && total >= 2){
        indexWidget.value = index + 1;

        if(autoQueue){
          await sleep(200);
          app.queuePrompt(0, 1);
        }
      }
      // 最後までいった
      else if(index + 1 >= total){
        indexWidget.value = 0;
      }
    };

  },

});
