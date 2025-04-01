import { app } from "/scripts/app.js";
import { $el } from "../../../scripts/ui.js";
import { findWidgetByName, sleep, getReadOnlyWidgetBase } from "./utils.js";


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
            
            const counterWidget = findWidgetByName(this, "counter");
            const promptWidget = findWidgetByName(this, "prompt");
            const commentTypeWidget = findWidgetByName(this, "comment_type");
            const commentTypeValue = commentTypeWidget.value;
        
            // commentTypeWidget.value の再定義
            Object.defineProperty(commentTypeWidget, 'value', {
                get() {
                    return commentTypeValue;
                },
                async set(newVal) {
                    const count = await getTokenCount(promptWidget.value, newVal);
                    counterWidget.setValue(count);
                }
            });
  

            if (promptWidget && counterWidget) {
                // 初期カウント取得
                setTimeout(async ()=>{
                    const count = await getTokenCount(promptWidget.value, commentTypeWidget.value);
                    counterWidget.setValue(count);
                }, 1000);
        
                // デバウンス処理用の変数
                let debounceTimer;
        
                // プロンプト変更時のイベントリスナー
                if (promptWidget.inputEl) {
                    // inputEl は textarea 要素
                    promptWidget.inputEl.addEventListener("input", () => {
                        // 既存のタイマーをクリア
                        clearTimeout(debounceTimer);
                        
                        // 新しいタイマーを設定 (1秒後に実行)
                        debounceTimer = setTimeout(async () => {
                            const count = await getTokenCount(promptWidget.value, commentTypeWidget.value);
                            counterWidget.setValue(count);
                        }, 1000);
                    });
                }
            }
        
            return r;
        }
    },

    getCustomWidgets(app) {
        return {
            D2_TOKEN_COUNTER(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase(node, "D2_TOKEN_COUNTER", inputName, 0);
        
                widget.draw = function(ctx, node, width, y) {
                    const text = `Token count: ${this.value}`;
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "12px Arial";
                    ctx.fillText(text, 20, y + 20);
                };
                node.addCustomWidget(widget);
                return widget;
            },
        };
    },
});
