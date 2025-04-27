import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./modules/utils.js";


app.registerExtension({
  name: "Comfy.D2.D2_XYStringToPlot",

  nodeCreated(node) {
    if (node.constructor.title == "D2 XY String To Plot"){
      if (node.widgets){
        const countWidget = findWidgetByName(node, "string_count");
        let widgetValue = countWidget.value;
        handleInputsVisibility(node, widgetValue, [
          {name:"string", type:"STRING"},
        ])
    

        // string_count.value の再定義
        Object.defineProperty(countWidget, 'value', {
          get() {
            return widgetValue;
          },
          set(newVal) {
            if (newVal !== widgetValue) {
              widgetValue = newVal;
              handleInputsVisibility(node, newVal, [
                {name:"string", type:"STRING"},
              ])
            }
          }
        });
      }
    }
  }
});
