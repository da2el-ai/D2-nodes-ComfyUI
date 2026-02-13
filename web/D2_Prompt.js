import { app } from "/scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { findWidgetByName, sleep, getReadOnlyWidgetBase } from "./modules/utils.js";


// カウンターの書き換え
const setCounterLabel = (widget, value) => {
    const newVal = "token_count: <%value%>".replace("<%value%>", value);
    widget.label = newVal;
    console.log("counterWidget", widget);
    console.log("counterWidget", widget.value);
};


app.registerExtension({
    name: "Comfy.D2.D2_Prompt",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Prompt") return;

        const getTokenCount = (prompt, commentType) => {
            // パラメーターに prompt を加えて POST で送信する
            return new Promise(async (resolve) => {
                try {
                    const url = '/D2/token-counter/get-count';
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ prompt: prompt, comment_type: commentType })
                    });
                    const data = await response.json();
                    resolve(data.count);
                } catch (error) {
                    console.error("Error getting token count:", error);
                    resolve(0);
                }
            });
        }

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;
            
            const promptWidget = findWidgetByName(this, "prompt");
            const commentTypeWidget = findWidgetByName(this, "comment_type");
            const commentTypeValue = commentTypeWidget.value;
            const counterWidget = findWidgetByName(this, "token_count");
            
            // commentTypeWidget.value の再定義
            Object.defineProperty(commentTypeWidget, 'value', {
                get() {
                    return commentTypeValue;
                },
                async set(newVal) {
                    if(counterWidget.value === true){
                        const count = await getTokenCount(promptWidget.value, newVal);
                        // counterWidget.setValue(count);
                        setCounterLabel(counterWidget, count);
                    }
                }
            });
  

            if (promptWidget && counterWidget) {
                // 初期カウント取得
                setTimeout(async ()=>{
                    if(counterWidget.value === true){
                        const count = await getTokenCount(promptWidget.value, commentTypeWidget.value);
                        // counterWidget.setValue(count);
                        setCounterLabel(counterWidget, count);
                    }
                }, 1000);
        
                // デバウンス処理用の変数
                let debounceTimer;
        
                // プロンプト変更時のイベントリスナー
                if (promptWidget.inputEl) {
                    // inputEl は textarea 要素
                    promptWidget.inputEl.addEventListener("input", () => {
                        // 既存のタイマーをクリア
                        clearTimeout(debounceTimer);
                        
                        if(counterWidget.value === true){
                            // 新しいタイマーを設定 (1秒後に実行)
                            debounceTimer = setTimeout(async () => {
                                const count = await getTokenCount(promptWidget.value, commentTypeWidget.value);
                                // counterWidget.setValue(count);
                                setCounterLabel(counterWidget, count);
                            }, 1000);
                        }
                    });
                }
            }
        
            return r;
        }
    },
});
