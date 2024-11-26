import { app } from "/scripts/app.js";
// import { ComfyWidgets } from "/scripts/widgets.js";
// import { findWidgetByName } from "./utils.js";
import { D2Lightbox } from "./util_lightbox.js";


app.registerExtension({
  name: "Comfy.D2.D2_PreviewImage",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 Preview Image") return;

    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;
        this.lightBox = new D2Lightbox();
        return r;
    };
  },

  getCustomWidgets(app) {

    return {
      D2_PREVIEW_IMAGE(node, inputName, inputData, app) {
        const widget = node.addWidget("button", "Popup Image", "", () => {
          if(node.images.length >= 1){
            console.log("D2_PREVIEW_IMAGE", node);
            node.lightBox.openLightbox(node.images, 0);
          }
        });
        // node.addCustomWidget(widget);
        return widget;
      },
    };
  },
});
