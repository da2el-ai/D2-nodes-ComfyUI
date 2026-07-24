import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./modules/utils.js";

const changeInputVisibility = (node, val) => {
    handleInputsVisibility(node, val, [{ name: "text", type: "STRING" }]);
};

///////////////////////////
///////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_TextConcat",

    nodeCreated(node) {
        if (node.constructor.title == "D2 Text Concat") {
            if (node.widgets) {
                const countWidget = findWidgetByName(node, "text_count");
                let widgetValue = countWidget.value;

                changeInputVisibility(node, widgetValue);

                // text_count.value の再定義
                Object.defineProperty(countWidget, "value", {
                    get() {
                        return widgetValue;
                    },
                    set(newVal) {
                        if (newVal !== widgetValue) {
                            widgetValue = newVal;
                            changeInputVisibility(node, newVal);
                        }
                    },
                });
            }
        }
    },
});
