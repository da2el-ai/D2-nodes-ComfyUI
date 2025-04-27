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
         * ノード実行時
         */
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = async function (message) {
            onExecuted?.apply(this, arguments);

            // seed更新
            const seedWidget = findWidgetByName(this, "queue_seed");
            if(seedWidget){
                seedWidget.setValue(Math.floor(Math.random()*100000));
            }
            
            const imageCount = message["image_count"][0];
            folderImageController.imageCount = imageCount;
            folderImageController.refreshImageCount();
        };

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const folderWidget = findWidgetByName(this, "folder");
            const extensionWidget = findWidgetByName(this, "extension");
            const imageCountWidget = findWidgetByName(this, "image_count");
            const autoQueueWidget = findWidgetByName(this, "auto_queue");
            folderImageController.initWidget(
                this.id,
                folderWidget,
                extensionWidget,
                imageCountWidget,
                autoQueueWidget
            );

            return r;
        };
    },

    /**
     * D2_FOLDER_IMAGE_COUNT 画像枚数を表示
     */
    // getCustomWidgets(app) {
    //     return {
    //         D2_FOLDER_IMAGE_COUNT(node, inputName, inputData, app) {
    //             const widget = getReadOnlyWidgetBase(node, "D2_FOLDER_IMAGE_COUNT", inputName, 0);

    //             widget.draw = function (ctx, node, width, y) {
    //                 const text = `Image count: ${this.value}`;
    //                 ctx.fillStyle = "#ffffff";
    //                 ctx.font = "12px Arial";
    //                 ctx.fillText(text, 20, y + 20);
    //             };
    //             node.addCustomWidget(widget);
    //             return widget;
    //         },
    //         D2_FOLDER_IMAGE_SEED(node, inputName, inputData, app) {
    //             const widget = getReadOnlyWidgetBase(node, "D2_FOLDER_IMAGE_SEED", inputName, 0);
        
    //             widget.draw = function(ctx, node, width, y) {
    //               const text = `Seed: ${this.value}`;
    //               ctx.fillStyle = "#ffffff";
    //               ctx.font = "12px Arial";
    //               ctx.fillText(text, 20, y + 20);
    //             };
    //             node.addCustomWidget(widget);
    //             return widget;
    //           },
    //             };
    // },
});
