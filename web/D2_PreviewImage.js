import { app } from "/scripts/app.js";
import { D2Lightbox } from "./modules/util_lightbox.js";
import { findWidgetByName } from "./modules/utils.js";


app.registerExtension({
  name: "Comfy.D2.D2_PreviewImage",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 Preview Image") return;

    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

        const previewBtnWidget = findWidgetByName(this, "popup_image");
        previewBtnWidget.callback = () => {
          if(this.images && this.images.length >= 1){
            D2Lightbox.openLightbox(this.images, 0);
          }
        };

        return r;
    };
  },
});
