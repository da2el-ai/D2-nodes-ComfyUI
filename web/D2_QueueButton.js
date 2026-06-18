import { app } from "../../scripts/app.js";
import { D2_FloatContainer, CSS_CLASS_BUTTON_BASE, CSS_CLSSS_BUTTON_PRIMARY, CSS_CLSSS_BUTTON_SECONDARY } from "./D2_FloatContainer.js";


const D2_QUEUE_DEFAULT_COUNT = "1,10";

/**
 * Queue Button を作るクラス
 */
class D2_QueueButton {
  floatContainer = undefined;

  constructor() {
    // フロートコンテナ（アクションバー収納を有効化）
    this.floatContainer = new D2_FloatContainer('D2_QueueButton', 50, 50, { enableDock: true });
    
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
   * @param {string} [settingValue] 設定値（onChange から渡される最新値）
   */
  resetButton(settingValue) {
    this.floatContainer.removeAllContent();
    this._createButtons(settingValue);
  }

  /**
   * ボタン作成
   * @param {string} [settingValue] 設定値（未指定時は設定ストアから読む）
   */
  _createButtons(settingValue) {
    const counts = D2_QueueButton._getCounts(settingValue);

    counts.forEach((count) => {
      const button = document.createElement("button");
      button.classList.add("p-button", ...CSS_CLASS_BUTTON_BASE.split(" "), ...CSS_CLSSS_BUTTON_PRIMARY.split(" "));
      button.textContent = count;
      this.floatContainer.addContent(button);

      button.addEventListener("click", function (event) {
        app.queuePrompt(event.shiftKey ? -1 : 0, count);
      });
    });
  }

  /**
   * 設定からボタン設定を読む
   * @param {string} [settingValue] 渡されたらこの値を使う。未指定時のみ設定ストアから読む
   *   （onChange 発火時点では設定ストアが旧値のままなので、引数の最新値を優先する）
   */
  static _getCounts(settingValue) {
    const setting = settingValue !== undefined
      ? settingValue
      : app.ui.settings.getSettingValue("D2.QueueButton.BatchCount", D2_QUEUE_DEFAULT_COUNT);
    if (!setting || setting.trim() === "") return [];

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
      queueButton.resetButton(value);
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
