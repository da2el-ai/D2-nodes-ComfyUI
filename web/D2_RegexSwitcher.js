import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
    name: "Comfy.D2.D2_RegexSwitcher",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Regex Switcher") return;

        const checkTextVisible = (isShow, widget) => {
            if (isShow === "True") {
                widget.type = "customtext";
            } else {
                widget.type = "converted-widget";
            }
        };

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            // 入力文字確認を読み込み専用にする
            const checkTextWidget = this.widgets?.find((w) => w.name === "text_check");
            checkTextWidget.inputEl.readOnly = true;
            checkTextWidget.inputEl.style.opacity = 0.5;

            // 入力確認の表示・非表示切り替え
            const showTextWidget = this.widgets?.find((w) => w.name === "show_text");
            showTextWidget.callback = (isShow) => {
                checkTextVisible(isShow, checkTextWidget)
            };
            
            // 前回の状態を引き継ぎ
            setTimeout(()=>{
                checkTextVisible(showTextWidget.value, checkTextWidget)
            },200);

            return r;
        };

        /**
         * ノード実行時
         */
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);
            const checkTextWidget = this.widgets?.find((w) => w.name === "text_check");
            checkTextWidget.value = message.text[0];
        };
    },
});
