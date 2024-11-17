import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./utils.js";


app.registerExtension({
  name: "Comfy.D2.D2_XYImageStack",

  nodeCreated(node) {
    if (node.constructor.title == "D2 XY Image Stack"){
      console.log("D2 XY Image Stack");
      console.log(node);

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
