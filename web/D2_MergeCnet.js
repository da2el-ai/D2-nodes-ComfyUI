import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./modules/utils.js";

/**
 * cnet_stack_count に応じて cnet_stack_1..N の入力を増減する
 */
const changeInputVisibility = (node, val) => {
    handleInputsVisibility(node, val, [{ name: "cnet_stack", type: "D2_CNET_STACK" }]);
};

///////////////////////////
///////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_MergeCnet",

    nodeCreated(node) {
        if (node.constructor.title == "D2 Merge Cnet") {
            if (node.widgets) {
                const countWidget = findWidgetByName(node, "cnet_stack_count");
                let widgetValue = countWidget.value;

                changeInputVisibility(node, widgetValue);

                // cnet_stack_count.value の再定義
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
