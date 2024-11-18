import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./utils.js";


app.registerExtension({
  name: "Comfy.D2.D2_ImageStack",

  nodeCreated(node) {
    if (node.constructor.title == "D2 Image Stack"){
      if (node.widgets){
        const countWidget = findWidgetByName(node, "image_count");
        let widgetValue = countWidget.value;
        handleInputsVisibility(node, widgetValue, ["image"], "IMAGE")

        // lora_count.value の再定義
        Object.defineProperty(countWidget, 'value', {
          get() {
            return widgetValue;
          },
          set(newVal) {
            if (newVal !== widgetValue) {
              widgetValue = newVal;
              handleInputsVisibility(node, newVal, ["image"], "IMAGE")
            }
          }
        });
      }
    }
  }
});
