import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./modules/utils.js";

const changeInputVisibility = (node, val) => {
  if (node.constructor.title == "D2 Image Mask Stack"){
    handleInputsVisibility(node, val, [
      {name:"image", type:"IMAGE"},
      {name:"mask", type:"MASK"},
    ])
  }else{
    handleInputsVisibility(node, val, [
      {name:"image", type:"IMAGE"},
    ])
  }
};

///////////////////////////
///////////////////////////
app.registerExtension({
  name: "Comfy.D2.D2_ImageStack",

  nodeCreated(node) {
    if (node.constructor.title == "D2 Image Stack" || node.constructor.title == "D2 Image Mask Stack"){
      if (node.widgets){
        const countWidget = findWidgetByName(node, "image_count");
        let widgetValue = countWidget.value;

        changeInputVisibility(node, widgetValue);

        // lora_count.value の再定義
        Object.defineProperty(countWidget, 'value', {
          get() {
            return widgetValue;
          },
          set(newVal) {
            if (newVal !== widgetValue) {
              widgetValue = newVal;
              changeInputVisibility(node, newVal);
            }
          }
        });
      }
    }
  }
});
