import { app } from "../../scripts/app.js";

const D2_QUEUE_DEFAULT_COUNT = "1,10";

/**
 * Queue Button を作るクラス
 */
class D2_QueueButton {
  static CSS_FILEPATH = "./extensions/D2-nodes-ComfyUI/css/D2_QueueButton.css";
  static COOKIE_NAME = "D2_QueueButton_Pos";
  static DEFAULT_LEFT = 50;
  static DEFAULT_TOP = 50;

  container = undefined;
  buttonContainer = undefined;

  constructor() {
    D2_QueueButton._loadStyles();
    this._createContainer();
    this._createButtons();

    // 表示切り替え
    const visible = app.ui.settings.getSettingValue("D2.QueueButton.Visible", true);
    this.changeVisible(visible);

    // 初期位置
    const pos = D2_QueueButton._getPosition();
    this.container.style.left = pos[0] + "px";
    this.container.style.top = pos[1] + "px";

    // ウィンドウリサイズ対策
    window.addEventListener("resize", () => {
      this.resizeSetting();
    });
    this.resizeSetting();
}

  /**
   * ボタンリセット
   */
  resetButton() {
    this.buttonContainer.innerHTML = "";
    this._createButtons();
  }

  /**
   * 表示切り替え
   */
  changeVisible(bool) {
    this.container.style.display = bool ? "block" : "none";
  }

  ///////////////////////////////////////////////
  // private method
  ///////////////////////////////////////////////
  /**
   * ベース作成
   */
  _createContainer() {
    this.container = document.createElement("div");
    this.container.classList.add("p-panel", "d2-queue-button");
    document.querySelector("body").appendChild(this.container);

    const content = document.createElement("div");
    content.classList.add("p-panel-content", "flex", "flex-nowrap", "items-center", "d2-queue-button__content");
    this.container.appendChild(content);

    const dragHandle = document.createElement("span");
    dragHandle.classList.add("drag-handle", "cursor-move", "mr-2");
    content.appendChild(dragHandle);

    this.buttonContainer = document.createElement("div");
    this.buttonContainer.classList.add("flex", "flex-nowrap", "items-center", "d2-queue-button__button-container");
    content.appendChild(this.buttonContainer);

    // ドラッグ設定
    this._dragSetting(dragHandle, this.container);
  }

  /**
   * ボタン作成
   */
  _createButtons() {
    const counts = D2_QueueButton._getCounts();

    counts.forEach((count) => {
      const button = document.createElement("button");
      button.classList.add("p-button");
      button.textContent = count;
      this.buttonContainer.appendChild(button);

      button.addEventListener("click", function (event) {
        app.queuePrompt(event.shiftKey ? -1 : 0, count);
      });
    });
  }

  /**
   * 設定からボタン設定を読む
   */
  static _getCounts(string) {
    const setting = app.ui.settings.getSettingValue("D2.QueueButton.BatchCount", D2_QUEUE_DEFAULT_COUNT);
    if (setting.trim() === "") return [];

    return setting
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item !== "")
      .map((item) => Number(item));
  }

  /**
   * CSSを動的に読み込む
   */
  static _loadStyles() {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = D2_QueueButton.CSS_FILEPATH;
    document.head.appendChild(link);
  }

  /**
   * 座標をcookieに記録
   */
  static _savePosition(x, y) {
    const jsonString = JSON.stringify([x, y]);
    const encodedJsonString = encodeURIComponent(jsonString);

    const farFuture = new Date();
    farFuture.setFullYear(farFuture.getFullYear() + 100);

    document.cookie = `${D2_QueueButton.COOKIE_NAME}=${encodedJsonString}; expires=${farFuture.toUTCString()}; path=/`;
  }

  /**
   * 座標をcookieから取得
   */
  static _getPosition() {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(D2_QueueButton.COOKIE_NAME + "=")) {
        const encodedJsonString = cookie.substring(D2_QueueButton.COOKIE_NAME.length + 1);
        const jsonString = decodeURIComponent(encodedJsonString);
        return JSON.parse(jsonString);
      }
    }
    // Cookieが見つからない場合
    return [D2_QueueButton.DEFAULT_LEFT, D2_QueueButton.DEFAULT_TOP];
  }

  /**
   * ドラッグ設定
   */
  _dragSetting(handle, container) {
    let isDragging = false;
    let startX, startY, initialLeft, initialTop;

    // マウスダウンイベントリスナー
    handle.addEventListener("mousedown", (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      initialLeft = container.offsetLeft;
      initialTop = container.offsetTop;

      // テキスト選択を防止
      e.preventDefault();
    });

    // マウスムーブイベントリスナー
    document.addEventListener("mousemove", (e) => {
      if (!isDragging) return;

      const x = e.clientX - startX + initialLeft;
      const y = e.clientY - startY + initialTop;

      container.style.left = `${x}px`;
      container.style.top = `${y}px`;

      D2_QueueButton._savePosition(x, y);
    });

    // マウスアップイベントリスナー
    document.addEventListener("mouseup", () => {
      isDragging = false;
    });

    // マウスリーブイベントリスナー（ブラウザ外にマウスが出た場合）
    document.addEventListener("mouseleave", () => {
      isDragging = false;
    });
  }

  /**
   * ウィンドウリサイズ対策
   */
  resizeSetting() {
    const container = this.container;
    const rect = container.getBoundingClientRect();
    const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;

    // 右端の調整
    if (rect.right > viewportWidth) {
        const newLeft = Math.max(0, viewportWidth - rect.width);
        container.style.left = `${newLeft}px`;
    } else if (rect.left < 0) {
        container.style.left = '0px';
    }

    // 下端の調整
    if (rect.bottom > viewportHeight) {
        const newTop = Math.max(0, viewportHeight - rect.height);
        container.style.top = `${newTop}px`;
    } else if (rect.top < 0) {
        container.style.top = '0px';
    }
  }
}

(function () {
  const queueButton = new D2_QueueButton();

  app.ui.settings.addSetting({
    id: "D2.QueueButton.BatchCount",
    name: "Batch count list",
    type: "string",
    defaultValue: D2_QUEUE_DEFAULT_COUNT,
    onChange(value) {
      queueButton.resetButton();
    },
  });

  app.ui.settings.addSetting({
    id: "D2.QueueButton.Visible",
    name: "Show queue button",
    type: "boolean",
    defaultValue: true,
    onChange(value) {
      queueButton.changeVisible(value);
    },
  });
})();
