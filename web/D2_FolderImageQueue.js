import { app } from "/scripts/app.js";
import { findWidgetByName, sleep, getReadOnlyWidgetBase, customWidgetDrawText } from "./modules/utils.js";

const API_BASE_URL = "/D2/folder-image-queue/";

class FolderImageQueue {
    folderWidget;
    extensionWidget;
    startAtWidget;
    imageCountWidget;
    autoQueueWidget;
    progressBarWidget;
    imageCount = 0;
    id = 0;

    /**
     * 対象画像枚数を取得
     */
    getImageCount() {
        return new Promise(async (resolve) => {
            const folder = this.folderWidget.value;
            const extension = this.extensionWidget.value;
            const url = API_BASE_URL + `get_image_count?folder=${folder}&extension=${extension}`;

            const response = await fetch(url);
            const data = await response.json();
            this.imageCount = parseInt(data["image_count"]);
            resolve(this.imageCount);
        });
    }

    /**
     * 開始番号を更新
     */
    countUpStartAt() {
        this.startAt = (this.startAt + 1) % this.imageCount;
        this.startAtWidget.value = this.startAt;
    }

    /**
     * ボタンテキストを書き換え
     */
    refreshImageCount() {
        this.imageCountWidget.setValue(this.imageCount);
    }

    /**
     * キュー実行処理
     * 残り画像があるなら次のキューを入れる
     * imageCount = 1 だったら何もしない
     * @param {int} imageCount 実行回数 (1から開始)
     * @param {int} startAt 現在の回数 (0から開始のインデックス)
     */
    async onExecuted(imageCount, startAt) {
        // 「まだ残りがある」条件: 現在の実行回数 (startAt + 1) が総実行回数 (imageCount) より小さい場合
        if (startAt + 1 < imageCount) {
            this.startAtWidget.value = startAt + 1;
            this.progressBarWidget.setValue((startAt + 1) / imageCount);

            // 自動キューが有効なら次のキューを実行
            if (this.autoQueueWidget.value) {
                await sleep(200);
                app.queuePrompt(0, 1);
            }
        }
        // 「最後までいった」条件: 現在の実行回数 (startAt + 1) が総実行回数 (imageCount) と同じかそれ以上の場合
        else if (startAt + 1 >= imageCount) {
            console.log(`D2 Folder Image Queue: 最後までいった (${startAt + 1} / ${imageCount})`);
            // 開始インデックスとプログレスバーをリセット
            this.startAtWidget.value = 0;
            this.progressBarWidget.setValue(0);
        }
    }

    /**
     * 入力フィールドのイベント設定
     * パス、拡張子が入力されたら枚数を取得する
     */
    initWidget(id, folderWidget, extensionWidget, startAtWidget, imageCountWidget, autoQueueWidget, progressBarWidget) {
        this.id = id;
        this.folderWidget = folderWidget;
        this.extensionWidget = extensionWidget;
        this.startAtWidget = startAtWidget;
        this.imageCountWidget = imageCountWidget;
        this.autoQueueWidget = autoQueueWidget;
        this.progressBarWidget = progressBarWidget;

        // イベント登録
        folderWidget.callback = async () => {
            await this.getImageCount();
            this.refreshImageCount();
        };
        extensionWidget.callback = async () => {
            await this.getImageCount();
            this.refreshImageCount();
        };

        // 初期表示変更
        setTimeout(async () => {
            await this.getImageCount();
            this.refreshImageCount();
        }, 100);
    }
}

/////////////////////////////////////////
/////////////////////////////////////////
/////////////////////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_FolderImageQueue",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Folder Image Queue") return;

        const folderImageQueue = new FolderImageQueue();

        /**
         * ノード実行時
         */
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = async function (message) {
            onExecuted?.apply(this, arguments);

            // seed更新
            const seedWidget = findWidgetByName(this, "queue_seed");
            seedWidget.updateSeed();
            
            const imageCount = message["image_count"][0];
            const startAt = message["start_at"][0];
            folderImageQueue.onExecuted(imageCount, startAt);
        };

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const progressBarWidget = findWidgetByName(this, "progress_bar");
            const folderWidget = findWidgetByName(this, "folder");
            const extensionWidget = findWidgetByName(this, "extension");
            const startAtWidget = findWidgetByName(this, "start_at");
            const imageCountWidget = findWidgetByName(this, "image_count");
            const autoQueueWidget = findWidgetByName(this, "auto_queue");
            folderImageQueue.initWidget(
                this.id,
                folderWidget,
                extensionWidget,
                startAtWidget,
                imageCountWidget,
                autoQueueWidget,
                progressBarWidget
            );

            return r;
        };
    },

    /**
     * D2_FOLDER_IMAGE_COUNT 画像枚数を表示
     */
    getCustomWidgets(app) {
        return {
            D2_FOLDER_IMAGE_COUNT(node, inputName, inputData, app) {
                const widget = getReadOnlyWidgetBase(node, "D2_FOLDER_IMAGE_COUNT", inputName, 0);

                widget.draw = function (ctx, node, width, y) {
                    customWidgetDrawText(ctx, y, `Image count: ${this.value}`);
                };
                node.addCustomWidget(widget);
                return widget;
            },
        };
    },
});
