import { app } from "../../scripts/app.js";
import { D2_FloatContainer, CSS_CLASS_BUTTON_BASE, CSS_CLSSS_BUTTON_PRIMARY, CSS_CLSSS_BUTTON_SECONDARY } from "./D2_FloatContainer.js";
import { loadCssFile } from "./modules/utils.js";


/**
 * プロンプト変換
 * nodes/modules/nai_prompt_util.py にも同じロジックがあるので、変更するときは両方を揃える
 */

class D2_PromptConvert {
    // ブレース1個あたりの倍率
    static RATE = 1.05;
    // SD 方式の weight 指定 (text:1.2)
    static SD_WEIGHT_PATTERN = /\(([^)]+):\s*(-?\d*\.?\d+)\s*\)/g;
    // NAI 方式の weight 開始 1.2:: と閉じ ::
    // 直前が英数字・_・. のときは aaa5:: や 2girls:: の語の一部なので weight 開始とみなさない
    static NAI_NUMBER_TOKEN_PATTERN = /(?<![\w.])(-?\d*\.?\d+)::|::/g;
    // NAI 方式のブレース {{aaa}} [[aaa]]
    static NAI_BRACE_PATTERN = /[\[{]+[^\]}]+[\]}]+/g;
    // weight 本文を 先頭の空白 / 中身 / 末尾の空白・カンマ に分ける
    static BODY_PATTERN = /^(\s*)([\s\S]*?)([\s,]*)$/;

    /**
     * 行ごとに変換関数を適用する（weight の範囲は改行を越えない）
     */
    static $_convertLines (prompt, convertLine) {
        return prompt.split("\n").map(convertLine).join("\n");
    }

    /**
     * StableDiffusionのweightをNAI方式に変換
     */
    static convertToNai (srcPrompt, convertType = "number") {
        return D2_PromptConvert.$_convertLines(srcPrompt, (line) => {
            return line.replace(D2_PromptConvert.SD_WEIGHT_PATTERN, (match, text, weightStr) => {
                return D2_PromptConvert.$_convertToNai(text.trim(), parseFloat(weightStr), convertType);
            });
        });
    }

    static $_convertToNai (text, weight, convertType = "number") {
        // ブレース方式は weight 0 以下を log で表せないので数値方式で出す
        if (convertType === "number" || weight <= 0) {
            // 閉じ :: の直前が数字だと aaa5:: の 5:: が weight 開始と誤解釈されるので空白を入れる
            return `${weight}::${text} ::`;
        }

        const count = Math.abs(Math.round(Math.log(weight) / Math.log(D2_PromptConvert.RATE)));
        if (weight < 1) {
            return "[".repeat(count) + text + "]".repeat(count);
        }
        return "{".repeat(count) + text + "}".repeat(count);
    }

    /**
     * NAIのweightをStableDiffusion方式に変換
     */
    static convertToSd (srcPrompt, convertType = "number", removeNegative = true) {
        if (convertType === "number") {
            return D2_PromptConvert.$_convertLines(srcPrompt, (line) => {
                return D2_PromptConvert.$_convertNumberLineToSd(line, removeNegative);
            });
        }
        return D2_PromptConvert.$_convertLines(srcPrompt, (line) => {
            return line.replace(D2_PromptConvert.NAI_BRACE_PATTERN, (match) => {
                return D2_PromptConvert.$_convertBraceToSd(match);
            });
        });
    }

    /**
     * 数値方式の1行を SD 方式に変換する
     * weight 開始と閉じ :: を先頭から順に拾い、閉じ忘れは次の weight 開始か行末で閉じる
     */
    static $_convertNumberLineToSd (line, removeNegative) {
        const result = [];
        let pos = 0;
        let openWeight = null;

        for (const m of line.matchAll(D2_PromptConvert.NAI_NUMBER_TOKEN_PATTERN)) {
            let body = line.substring(pos, m.index);
            if (m[1] === undefined && openWeight !== null) {
                // 閉じ :: 直前の空白は convertToNai が誤解釈防止で入れたものなので捨てる
                body = body.trimEnd();
            }
            result.push(D2_PromptConvert.$_closeWeight(body, openWeight, removeNegative));
            if (m[1] !== undefined) {
                openWeight = parseFloat(m[1]);
            } else if (openWeight !== null) {
                openWeight = null;
            } else {
                // 対応する weight 開始がない :: は文字として残す
                result.push("::");
            }
            pos = m.index + m[0].length;
        }

        result.push(D2_PromptConvert.$_closeWeight(line.substring(pos), openWeight, removeNegative));
        return result.join("");
    }

    /**
     * weight の本文を (text:weight) にする。weight が開いていなければ本文をそのまま返す
     */
    static $_closeWeight (body, weight, removeNegative) {
        if (weight === null) {
            return body;
        }

        const [, lead, text, trail] = body.match(D2_PromptConvert.BODY_PATTERN);
        if (text === "" || (weight < 0 && removeNegative)) {
            return lead + trail;
        }
        return `${lead}(${text}:${weight})${trail}`;
    }

    /**
     * ブレース方式 {{aaa}} [[aaa]] 1個を SD 方式に変換する
     */
    static $_convertBraceToSd (prompt) {
        const braCount = (prompt.match(/[\[{]/g) || []).length;
        let weight;
        if (prompt[0] === "{") {
            weight = Math.pow(D2_PromptConvert.RATE, braCount);
        } else {
            weight = Math.pow(1 / D2_PromptConvert.RATE, braCount);
        }

        const weightAdjust = Math.round(weight * 10) / 10;
        const text = prompt.replace(/[\[\]{}]+/g, "");
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
    convertType = "number"; // デフォルト値
    removeNegative = true;

    constructor() {
        this._createDialog();
        loadCssFile(D2_PromptConvertDialog.CSS_FILEPATH);
    }

    /**
     * モーダルの表示
     */
    showModal () {
        // this.container.showModal();
        this.container.style.display = "block";
    }

    _createDialog () {
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
        const sdToNaiBtn = D2_PromptConvertDialog.createButton("SD 👉 NAI", () => {
            const prompt = sdPrompt.value;
            const newPrompt = D2_PromptConvert.convertToNai(prompt, this.convertType);
            naiPrompt.value = newPrompt;
        });
        content.appendChild(sdToNaiBtn);

        // NAI > SD 変換ボタン
        const naiToSdBtn = D2_PromptConvertDialog.createButton("SD 👈 NAI", () => {
            const prompt = naiPrompt.value;
            const newPrompt = D2_PromptConvert.convertToSd(prompt, this.convertType, this.removeNegative);
            sdPrompt.value = newPrompt;
        });
        content.appendChild(naiToSdBtn);

        // SDクリップボード
        const copySdBtn = D2_PromptConvertDialog.createButton("📋 Copy SD and ❌ close", () => {
            sdPrompt.select();
            document.execCommand("copy");
            this.container.style.display = "none";
        });
        content.appendChild(copySdBtn);

        // NAIクリップボード
        const copyNaiBtn = D2_PromptConvertDialog.createButton("📋 Copy NAI and ❌ close", () => {
            naiPrompt.select();
            document.execCommand("copy");
            this.container.style.display = "none";
        });
        content.appendChild(copyNaiBtn);

        // 閉じるボタン
        const closeBtn = document.createElement("button");
        closeBtn.classList.add("d2-prompt-convert__close-btn");
        closeBtn.textContent = "❌ Close";
        closeBtn.addEventListener("click", () => {
            // container.close();
            this.container.style.display = "none";
        });
        content.appendChild(closeBtn);

        // 方式切り替えラジオボタン
        const radioButtons = this.createRadioButtons();
        content.appendChild(radioButtons);

    }

    /**
     * プロンプトエリア作成
     * @param {string} placeholder 
     * @returns HTMLElement
     */
    static createPromptArea (placeholder) {
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
    static createButton (text, onClick) {
        const btn = document.createElement("button");
        btn.classList.add("d2-prompt-convert__btn");
        btn.textContent = text;
        btn.addEventListener("click", () => {
            onClick();
        });
        return btn;
    }

    /**
     * ラジオボタンコンテナ作成
     * @returns HTMLElement
     */
    createRadioButtons () {
        const radioContainer = document.createElement("div");
        radioContainer.classList.add("d2-prompt-convert__radio-container");
        radioContainer.style.cssText = `
            margin: 10px 0;
            display: flex;
            gap: 20px;
            align-items: center;
            justify-content: center;
            grid-column: span 2;
        `;

        const braceTypeLabel = document.createElement("label");
        braceTypeLabel.htmlFor = "braceType";
        braceTypeLabel.textContent = "brace";
        braceTypeLabel.style.cssText = `
            margin-left: 5px;
            cursor: pointer;
            color: var(--input-text);
        `;

        const braceTypeRadio = document.createElement("input");
        braceTypeRadio.type = "radio";
        braceTypeRadio.name = "convertType";
        braceTypeRadio.id = "braceType";
        braceTypeRadio.value = "brace";
        braceTypeRadio.checked = false;
        braceTypeRadio.addEventListener("change", () => {
            if (braceTypeRadio.checked) {
                this.convertType = "brace";
            }
        });
        braceTypeLabel.prepend(braceTypeRadio);

        const numberTypeLabel = document.createElement("label");
        numberTypeLabel.htmlFor = "numberType";
        numberTypeLabel.textContent = "number";
        numberTypeLabel.style.cssText = `
            margin-left: 5px;
            cursor: pointer;
            color: var(--input-text);
        `;

        const numberTypeRadio = document.createElement("input");
        numberTypeRadio.type = "radio";
        numberTypeRadio.name = "convertType";
        numberTypeRadio.id = "numberType";
        numberTypeRadio.value = "number";
        numberTypeRadio.checked = true;
        numberTypeRadio.addEventListener("change", () => {
            if (numberTypeRadio.checked) {
                this.convertType = "number";
            }
        });
        numberTypeLabel.prepend(numberTypeRadio);

        // NAI > SD の number 方式でだけ効く
        const removeNegativeLabel = document.createElement("label");
        removeNegativeLabel.htmlFor = "removeNegative";
        removeNegativeLabel.textContent = "Remove negative";
        removeNegativeLabel.style.cssText = `
            margin-left: 5px;
            cursor: pointer;
            color: var(--input-text);
        `;

        const removeNegativeCheckbox = document.createElement("input");
        removeNegativeCheckbox.type = "checkbox";
        removeNegativeCheckbox.id = "removeNegative";
        removeNegativeCheckbox.checked = this.removeNegative;
        removeNegativeCheckbox.addEventListener("change", () => {
            this.removeNegative = removeNegativeCheckbox.checked;
        });
        removeNegativeLabel.prepend(removeNegativeCheckbox);

        radioContainer.appendChild(numberTypeLabel);
        radioContainer.appendChild(braceTypeLabel);
        radioContainer.appendChild(removeNegativeLabel);

        return radioContainer;
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
    changeVisible (bool) {
        this.floatContainer.changeVisible(bool);
    }

    /**
     * ボタン作成
     */
    _createButton () {
        const button = document.createElement("button");
        button.classList.add("p-button", ...CSS_CLASS_BUTTON_BASE.split(" "), ...CSS_CLSSS_BUTTON_PRIMARY.split(" "));
        button.textContent = "Prompt convert";
        this.floatContainer.addContent(button);

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
        onChange (value) {
            promptConvertButton.changeVisible(value);
        },
    });
})();
