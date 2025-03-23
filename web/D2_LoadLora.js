import { app } from "/scripts/app.js";
import { findWidgetByName, handleWidgetsVisibility } from "./utils.js";

app.registerExtension({
  name: "Comfy.D2.D2_LoadLora",

  nodeCreated(node) {
    if (node.constructor.title !== "D2 Load Lora") return;
    if (!node.widgets) return;

    // loraを選択してテキストエリアに埋め込む
    const defaultValue = "CHOOSE";
    const chooserWidget = findWidgetByName(node, "insert_lora");
    const textWidget =  findWidgetByName(node, "lora_text");
    const modeWidget =  findWidgetByName(node, "mode");

    Object.defineProperty(chooserWidget, 'value', {
      get() {
        return defaultValue;
      },
      set(newVal) {
        if (newVal !== defaultValue) {
          if(modeWidget.value === "simple"){
            textWidget.value += `\n${newVal}:1`;
          } else {
            textWidget.value += `\n<lora:${newVal}:1>`;
          }
          chooserWidget.value = "CHOOSE";
          textWidget.inputEl.focus();
        }
      }
    });

  },
});
