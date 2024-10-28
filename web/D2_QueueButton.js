import { app } from "../../scripts/app.js";
import { D2_FloatContainer } from "./D2_FloatContainer.js";


const D2_QUEUE_DEFAULT_COUNT = "1,10";

/**
 * Queue Button を作るクラス
 */
class D2_QueueButton {
  floatContainer = undefined;

  constructor() {
    // フロートコンテナ
    this.floatContainer = new D2_FloatContainer('D2_QueueButton', 50, 50);
    
    this._createButtons();

    // 表示切り替え
    const visible = app.ui.settings.getSettingValue("D2.QueueButton.Visible", true);
    this.changeVisible(visible);
}

  /**
   * 表示切り替え
   */
  changeVisible(bool) {
    this.floatContainer.changeVisible(bool);
  }

  /**
   * ボタンリセット
   */
  resetButton() {
    this.floatContainer.removeButtons();
    this._createButtons();
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
      this.floatContainer.addButton(button);

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
