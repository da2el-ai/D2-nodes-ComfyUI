import { app } from "/scripts/app.js";
import { findWidgetByName, findWidgetByType } from "./utils.js";

const BUTTON_NAME = "Queue 0 images";
const API_BASE_URL = "/D2/folder-image-queue/";

class FolderImageQueue {
  folderWidget;
  extensionWidget;
  startAtWidget;
  batchCountWidget;
  queueButton;
  imageCount = 0;
  startAt = 0;
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
   * 開始番号を取得
   */
  getStartAt() {
    this.startAt = parseInt(this.startAtWidget.value);
    return this.startAt;
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
  refreshButtonText() {
    this.queueButton.name = `Queue (${this.imageCount} - ${this.startAt}) images`;
  }

  // 待機用の関数
  sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  /**
   * キューを実行
   */
  async execQueue() {
    // 枚数を取得してボタンを書き換えた後にキューを実行
    const imageCount = await this.getImageCount();
    const startAt = this.startAt;
    const queueCount = imageCount - startAt;
    this.refreshButtonText();

    for (let i = startAt; i < imageCount; i++) {
      app.queuePrompt(0, this.batchCountWidget.value);
      this.countUpStartAt();
      await this.sleep(200);
    }
  }

  /**
   * 入力フィールドのイベント設定
   * パス、拡張子が入力されたら枚数を取得する
   */
  initWidget(id, folderWidget, extensionWidget, startAtWidget, batchCountWidget, queueButton) {
    this.id = id;
    this.folderWidget = folderWidget;
    this.extensionWidget = extensionWidget;
    this.startAtWidget = startAtWidget;
    this.batchCountWidget = batchCountWidget;
    this.queueButton = queueButton;

    // イベント登録
    folderWidget.callback = async () => {
      await this.getImageCount();
      this.refreshButtonText();
    };
    extensionWidget.callback = async () => {
      await this.getImageCount();
      this.refreshButtonText();
    };
    startAtWidget.callback = () => {
      startAtWidget.value = startAtWidget.value % this.imageCount;
      this.getStartAt();
      this.refreshButtonText();
    };
    queueButton.callback = () => {
      this.execQueue();
    };

    // 初期表示変更
    setTimeout(async () => {
      await this.getImageCount();
      this.getStartAt();
      this.refreshButtonText();
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
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, arguments);
      // populate.call(this, message.text);
      // console.log("onExecuted");
      // console.log(message);
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
      const startAtWidget = findWidgetByName(this, "start_at");
      const batchCountWidget = findWidgetByName(this, "batch_count");
      const queueButton = findWidgetByType(this, "button");
      folderImageQueue.initWidget(this.id, folderWidget, extensionWidget, startAtWidget, batchCountWidget, queueButton);
      return r;
    };
  },

  /**
   * D2_FOLDER_IMAGE_QUEUE ボタンを作成
   */
  getCustomWidgets(app) {
    return {
      D2_FOLDER_IMAGE_QUEUE(node, inputName, inputData, app) {
        const widget = node.addWidget("button", BUTTON_NAME, 0, () => {});
        return widget;
      },
    };
  },
});
