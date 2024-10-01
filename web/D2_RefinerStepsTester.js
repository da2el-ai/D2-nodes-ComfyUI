import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
  name: "Comfy.D2.D2_RefinerStepsTester",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "D2 Refiner Steps Tester") return;

    // 以下、カスタムノード処理
    function populate(text) {
      // すでに表示しているものがあれば削除
      if (this.widgets) {
        this.widgets.forEach((widget) => {
          widget.onRemove?.();
        });
        this.widgets.length = 0;
      }

      // 文字列はなぜか配列で送られてくるので結合
      const showText = text.join("");
      const widget = ComfyWidgets["STRING"](
        this,
        "text",
        ["STRING", { multiline: true }],
        app
      ).widget;
      widget.inputEl.readOnly = true;
      widget.inputEl.style.opacity = 0.6;
      widget.value = showText;
    }

    /**
     * ノード実行時
     */
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, arguments);
      populate.call(this, message.text);
    };
  },
});
