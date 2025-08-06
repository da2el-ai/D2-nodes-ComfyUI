import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./modules/utils.js";

const changeInputVisibility = (node, val) => {
    handleInputsVisibility(node, val, [{ name: "arg", type: "*" }]);
};

///////////////////////////
///////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_FilenameTemplate",

    nodeCreated(node) {
        if (node.constructor.title == "D2 Filename Template" || node.constructor.title == "D2 Filename Template2") {
            if (node.widgets) {
                const countWidget = findWidgetByName(node, "arg_count");
                let widgetValue = countWidget.value;

                changeInputVisibility(node, widgetValue);

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
