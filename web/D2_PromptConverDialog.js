import { app } from "../../scripts/app.js";
import { D2_FloatContainer } from "./D2_FloatContainer.js";
import { loadCssFile } from "./modules/utils.js";


/**
 * プロンプト変換
 */

class D2_PromptConvert {
  static RATE = 1.05;

  /**
   * StableDiffusionのweightをNAI方式に変換
   */
  static convertToNai(srcPrompt) {
      const tempPrompt = srcPrompt.replace(/\n/g, '');
      const convertedPrompt = tempPrompt.replace(/\([^)]+:\s*[0-9.]+\s*\)/g, D2_PromptConvert.$_convertToNai);
      return convertedPrompt;
  }

  static $_convertToNai(prompt) {
      const parts = prompt.substring(1, prompt.length - 1).split(':');
      const text = parts.slice(0, -1).join(':').trim();
      const weightStr = parts[parts.length - 1].trim();
      const weight = parseFloat(weightStr);
      const n = Math.round(Math.log(weight) / Math.log(D2_PromptConvert.RATE));
      const count = Math.abs(n);

      let openBra, closeBra;
      if (weight < 1) {
          openBra = '[';
          closeBra = ']';
      } else {
          openBra = '{';
          closeBra = '}';
      }

      return openBra.repeat(count) + text + closeBra.repeat(count);
  }

  /**
   * NAIのweightをStableDiffusion方式に変換
   */
  static convertToSd(srcPrompt) {
      let tempPrompt = srcPrompt.replace(/\n/g, '');
      let convertedPrompt = tempPrompt.replace(/[\[{]+[^\]}]+[\]}]+/g, D2_PromptConvert.$_convertToSd);
      return convertedPrompt;
  }

  static $_convertToSd(prompt) {
      const braType = prompt.substring(0, 1);
      const braCount = (prompt.match(/[\[{]/g) || []).length;
      let weight = 0;

      if (braType === '{') {
          weight = 1 * Math.pow(D2_PromptConvert.RATE, braCount);
      } else {
          weight = 1 * Math.pow(1 / D2_PromptConvert.RATE, braCount);
      }

      let weightAdjust;

      // 四捨五入して小数点２位にするか、
      // 四捨五入せず小数点３位で切り捨てるか
      weightAdjust = Math.round(weight * 10) / 10;
      // if (opts.d2_npc_enable_rounding) {
      //     weightAdjust = Math.round(weight * 10) / 10;
      // } else {
      //     weightAdjust = Math.floor(weight * 100) / 100;
      // }

      const text = prompt.replace(/[\[\]{}]+/g, '');
      return `(${text}:${weightAdjust})`;
  }
}

/////////////////////////////////////////////
/////////////////////////////////////////////
/////////////////////////////////////////////

/**
 * プロンプト変換ダイアログ
 */
class D2_PromptConvertDialog {
    static CSS_FILEPATH = "/D2/assets/css/D2_PromptConvertDialog.css";

    container = undefined;

    constructor() {
        this._createDialog();
        loadCssFile(D2_PromptConvertDialog.CSS_FILEPATH);
    }

    /**
     * モーダルの表示
     */
    showModal() {
        // this.container.showModal();
        this.container.style.display   = "block";
      }
  
    _createDialog() {
      this.container = document.createElement("div");
        this.container.classList.add("comfy-modal", "d2-prompt-convert");
        document.body.appendChild(this.container);

        const content = document.createElement("div");
        content.classList.add("d2-prompt-convert__content");
        this.container.appendChild(content);

        const sdPrompt = D2_PromptConvertDialog.createPromptArea("input StableDiffusion Prompt");
        content.appendChild(sdPrompt);

        const naiPrompt = D2_PromptConvertDialog.createPromptArea("Input NovelAI Prompt");
        content.appendChild(naiPrompt);

        // SD > NAI 変換ボタン
        const sdToNaiBtn = D2_PromptConvertDialog.createButton("SD to NAI", () => {
            const prompt = sdPrompt.value;
            const newPrompt = D2_PromptConvert.convertToNai(prompt);
            naiPrompt.value = newPrompt;
        });
        content.appendChild(sdToNaiBtn);

        // NAI > SD 変換ボタン
        const naiToSdBtn = D2_PromptConvertDialog.createButton("NAI to SD", () => {
            const prompt = naiPrompt.value;
            const newPrompt = D2_PromptConvert.convertToSd(prompt);
            sdPrompt.value = newPrompt;
        });
        content.appendChild(naiToSdBtn);

        // SDクリップボード
        const copySdBtn = D2_PromptConvertDialog.createButton("Send SD to Clipboard", () => {
            sdPrompt.select();
            document.execCommand("copy");
        });
        content.appendChild(copySdBtn);

        // NAIクリップボード
        const copyNaiBtn = D2_PromptConvertDialog.createButton("Send NAI to Clipboard", () => {
            naiPrompt.select();
            document.execCommand("copy");
        });
        content.appendChild(copyNaiBtn);

        // 閉じるボタン
        const closeBtn = document.createElement("button");
        closeBtn.classList.add("d2-prompt-convert__close-btn");
        closeBtn.textContent = "CLOSE";
        closeBtn.addEventListener("click", () => {
            // container.close();
            this.container.style.display = "none";
        });
        content.appendChild(closeBtn);
    }

    /**
     * プロンプトエリア作成
     * @param {string} placeholder 
     * @returns HTMLElement
     */
    static createPromptArea(placeholder) {
        const textArea = document.createElement("textarea");
        textArea.classList.add("comfy-multiline-input", "d2-prompt-convert__prompt-area");
        textArea.placeholder = placeholder;
        return textArea;
    }

    /**
     * ボタン作成
     * @param {string} text 
     * @param {function} onClick 
     * @returns 
     */
    static createButton(text, onClick) {
        const btn = document.createElement("button");
        btn.classList.add("d2-prompt-convert__btn");
        btn.textContent = text;
        btn.addEventListener("click", () => {
            onClick();
        });
        return btn;
    }
}

///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////

/**
 * ダイアログ表示ボタン
 */
class D2_PromptConvertButton {
    floatContainer = undefined;
    dialog = undefined;

    constructor() {
        // フロートコンテナ
        this.floatContainer = new D2_FloatContainer("D2_PromptConvertBUtton", 50, 100);
        // ダイアログ
        this.dialog = new D2_PromptConvertDialog();

        this._createButton();

        // 表示切り替え
        const visible = app.ui.settings.getSettingValue("D2.PromptConvertButton.Visible", false);
        this.changeVisible(visible);
    }

    /**
     * 表示切り替え
     */
    changeVisible(bool) {
        this.floatContainer.changeVisible(bool);
    }

    /**
     * ボタン作成
     */
    _createButton() {
        const button = document.createElement("button");
        button.classList.add("p-button");
        button.textContent = "Prompt convert";
        this.floatContainer.addButton(button);

        button.addEventListener("click", () => {
          this.dialog.showModal();
        });
    }
}

(function () {
    const promptConvertButton = new D2_PromptConvertButton();

    app.ui.settings.addSetting({
        id: "D2.PromptConvertButton.Visible",
        name: "Show prompt convert button",
        type: "boolean",
        defaultValue: false,
        onChange(value) {
            promptConvertButton.changeVisible(value);
        },
    });
})();
