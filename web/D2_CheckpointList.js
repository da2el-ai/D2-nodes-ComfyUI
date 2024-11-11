import { app } from "/scripts/app.js";
import { findWidgetByName, handleWidgetsVisibility } from "./utils.js";


app.registerExtension({
  name: "Comfy.D2.D2_CheckpointList",

  nodeCreated(node) {
    if (node.constructor.title == "D2 Checkpoint List"){
      if (node.widgets){
        const countWidget = findWidgetByName(node, "ckpt_count");
        let widgetValue = countWidget.value;
        handleWidgetsVisibility(node, widgetValue, ["ckpt_name"])

        // ckpt_count.value の再定義
        Object.defineProperty(countWidget, 'value', {
          get() {
            return widgetValue;
          },
          set(newVal) {
            if (newVal !== widgetValue) {
              widgetValue = newVal;
              handleWidgetsVisibility(node, newVal, ["ckpt_name"])
            }
          }
        });
      }
    }
  }
});
