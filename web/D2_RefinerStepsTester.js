import { app } from "/scripts/app.js";
// import { ComfyWidgets } from "/scripts/widgets.js";
import { findWidgetByName } from "./modules/utils.js";

app.registerExtension({
  name: "Comfy.D2.D2_RefinerStepsTester",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 Refiner Steps Tester") return;

    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

        const textWidget = findWidgetByName(this, "text");
        textWidget.inputEl.readOnly = true;
        textWidget.inputEl.style.opacity = 0.6;

        return r;
    };

    /**
     * ノード実行時
     */
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, arguments);

      const textWidget = findWidgetByName(this, "text");
      textWidget.value = message["text"][0];
    };
  },
});
