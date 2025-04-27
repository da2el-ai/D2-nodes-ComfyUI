import { app } from "/scripts/app.js";
// import { ComfyWidgets } from "/scripts/widgets.js";
import { findWidgetByName } from "./modules/utils.js";

app.registerExtension({
  name: "Comfy.D2.D2_GetImageSize",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 Get Image Size") return;

    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;
        const displayWidget = findWidgetByName(this, "display");
        displayWidget.inputEl.readOnly = true;
        displayWidget.inputEl.style.opacity = 0.6;
        displayWidget.inputEl.style.height = "3em";
        return r;
    };

    /**
     * ノード実行時
     */
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, arguments);

      const w = message["width"][0];
      const h = message["height"][0];

      const displayWidget = findWidgetByName(this, "display");
      displayWidget.value = `width: ${w}\nheight: ${h}`;
    };
  },
});
