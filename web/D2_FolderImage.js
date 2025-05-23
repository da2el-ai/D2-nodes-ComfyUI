import { app } from "/scripts/app.js";
// import { $el } from "../../../scripts/ui.js";
import { findWidgetByName, sleep, getReadOnlyWidgetBase } from "./modules/utils.js";

const API_BASE_URL = "/D2/folder-image-queue/";

class FolderImageController {
    folderWidget;
    extensionWidget;
    imageCountWidget;
    autoQueueWidget;
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
     * テキストを書き換え
     */
    refreshImageCount() {
        this.imageCountWidget.setValue(this.imageCount);
    }

    /**
     * 入力フィールドのイベント設定
     * パス、拡張子が入力されたら枚数を取得する
     */
    initWidget(id, folderWidget, extensionWidget, imageCountWidget, autoQueueWidget) {
        this.id = id;
        this.folderWidget = folderWidget;
        this.extensionWidget = extensionWidget;
        this.imageCountWidget = imageCountWidget;
        this.autoQueueWidget = autoQueueWidget;

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
    name: "Comfy.D2.D2_FolderImages",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 XY Folder Images" && nodeData.name !== "D2 Load Folder Images") return;

        const folderImageController = new FolderImageController();

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const folderWidget = findWidgetByName(this, "folder");
            const extensionWidget = findWidgetByName(this, "extension");
            const autoQueueWidget = findWidgetByName(this, "auto_queue");
            const imageCountWidget = findWidgetByName(this, "image_count");
            imageCountWidget.textTemplate = "Image count: <%value%>"

            // seed と画像点数をリフレッシュ
            const seedWidget = findWidgetByName(this, "queue_seed");
            const refreshBtnWidget = findWidgetByName(this, "refresh_btn");
            refreshBtnWidget.name = "Get image count";
            refreshBtnWidget.callback = async () => {
                seedWidget.updateSeed();
                await folderImageController.getImageCount();
                folderImageController.refreshImageCount();
            };

            folderImageController.initWidget(
                this.id,
                folderWidget,
                extensionWidget,
                imageCountWidget,
                autoQueueWidget
            );

            return r;
        };
        
        /**
         * ノード実行時
         */
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = async function (message) {
            onExecuted?.apply(this, arguments);

            // // seed更新
            // const seedWidget = findWidgetByName(this, "queue_seed");
            // seedWidget.updateSeed();
            
            const imageCount = message["image_count"][0];
            folderImageController.imageCount = imageCount;
            folderImageController.refreshImageCount();
        };
    },
});
