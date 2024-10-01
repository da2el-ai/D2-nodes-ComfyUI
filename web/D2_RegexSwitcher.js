import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
    name: "Comfy.D2.D2_RegexSwitcher",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Regex Switcher") return;

        // 以下、カスタムノード処理
        function populate(text) {
            // 確認用ウィジェットがすでにあれば削除、なければ作る
            // すでに表示しているものがあれば削除
            if (this.widgets) {
                let index = this.widgets.findIndex((widget) => widget.name === "text_check");

                if (index >= 0) {
                    const widget = this.widgets[index];
                    this.widgets.splice(index, 1);
                    widget?.onRemove();
                }

                const newWidget = ComfyWidgets["STRING"](
                    this,
                    "text_check",
                    ["STRING", { multiline: true }],
                    app
                ).widget;
                newWidget.inputEl.readOnly = true;
                newWidget.inputEl.style.opacity = 0.6;

                // 文字列はなぜか配列で送られてくるので結合
                const showText = text.join("");
                newWidget.value = showText;
            }
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
