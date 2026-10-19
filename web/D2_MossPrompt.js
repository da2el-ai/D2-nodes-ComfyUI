import { app } from "/scripts/app.js";
import { findWidgetByName, handleInputsVisibility } from "./modules/utils.js";

/**
 * item_count に応じて moss_item_1..N の入力を増減する
 */
const changeInputVisibility = (node, val) => {
    handleInputsVisibility(node, val, [{ name: "moss_item", type: "D2_MOSS_ITEM" }]);
};

///////////////////////////
///////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_MossPrompt",

    nodeCreated(node) {
        if (node.constructor.title == "D2 Moss Prompt") {
            if (node.widgets) {
                const countWidget = findWidgetByName(node, "item_count");
                let widgetValue = countWidget.value;

                changeInputVisibility(node, widgetValue);

                // item_count.value の再定義
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
