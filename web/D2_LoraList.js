import { app } from "/scripts/app.js";
import { findWidgetByName, handleWidgetsVisibility } from "./utils.js";


app.registerExtension({
  name: "Comfy.D2.D2_XYLoraList",

  nodeCreated(node) {
    if (node.constructor.title == "D2 XY Lora List"){
      if (node.widgets){
        const countWidget = findWidgetByName(node, "lora_count");
        let widgetValue = countWidget.value;
        handleWidgetsVisibility(node, widgetValue, ["lora_name"])

        // lora_count.value の再定義
        Object.defineProperty(countWidget, 'value', {
          get() {
            return widgetValue;
          },
          set(newVal) {
            if (newVal !== widgetValue) {
              widgetValue = newVal;
              handleWidgetsVisibility(node, newVal, ["lora_name"])
            }
          }
        });
      }
    }
  }
});
