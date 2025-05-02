import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { D2_FloatContainer } from "./D2_FloatContainer.js";
import { D2Lightbox } from "./modules/util_lightbox.js";
import { sleep, loadCssFile, getImageUrlFromApi } from "./modules/utils.js";


const CSS_FILEPATH = "/D2/assets/css/D2_ProgressPreview.css";
loadCssFile(CSS_FILEPATH);


/**
 * Progress Preview を作るクラス
 */
class D2_ProgressPreview {
  floatContainer = undefined;
  progressPreviewBlobUrl = undefined;
  previewImage = undefined;
  images = []; // 画像URLを保持する配列
  _boundShowProgressPreview = null;
  _boundShowSuccessPreview = null;
  _boundHandlePreviewClick = null; // クリックハンドラ用のバインド
  _lastPromptId = undefined;
  _titleElement = undefined;

  constructor() {
    // イベントハンドラをバインド
    this._boundShowProgressPreview = ({detail}) => this._showProgressPreview(detail);
    this._boundShowSuccessPreview = ({detail}) => this._showSuccessPreview(detail);
    this._boundHandlePreviewClick = () => this._handlePreviewClick(); // クリックハンドラをバインド

    // フロートコンテナ
    this.floatContainer = new D2_FloatContainer('D2_ProgressPreview', 50, 50);
    
    this._createPreview();

    // 表示切り替え
    const visible = app.ui.settings.getSettingValue("D2.ProgressPreview.Visible", true);
    this.changeVisible(visible);
}

  /**
   * 表示切り替え
   */
  changeVisible(bool) {
    this.floatContainer.changeVisible(bool);

    if(bool){
      api.addEventListener("b_preview", this._boundShowProgressPreview);
      api.addEventListener("execution_success", this._boundShowSuccessPreview);
    }else{
      api.removeEventListener("b_preview", this._boundShowProgressPreview);
      api.removeEventListener("executed", this._boundShowSuccessPreview);
    }
  }

  /**
 * 生成完了イベント
 */
  async _showSuccessPreview(detail){

    // プロンプトIDが存在しなければ何もしない
    if(!detail.prompt_id) return;
    // 同じプロンプトIDが処理済みなら何もしない
    if(this._lastPromptId === detail.prompt_id) return;

    this._lastPromptId = detail.prompt_id;
    await sleep(200);

    this.images = []; // 画像リストをリセット

    try {
      const promptId = detail.prompt_id;
      const historyUrl = api.apiURL(`/history/${promptId}`);
      const response = await fetch(historyUrl);
      const data = await response.json();

      if (data[promptId] && data[promptId].outputs) {
        // 画像を取得
        for (const nodeId in data[promptId].outputs) {
          const output = data[promptId].outputs[nodeId];
          if (output.images) {
            for (const image of output.images) {
              const imageUrl = getImageUrlFromApi(image.filename, image.type);
              // imageUrl が既にリストに存在しないかチェック
              if (!this.images.includes(imageUrl)) {
                this.images.push(imageUrl);
              }
            }
          }
        }
      }

      if (this.images.length > 0) {
        // 最初の画像をプレビューに表示
        this._showImage(this.images[0]);
        this.previewImage.dataset.clickable = 'true'; // クリック可能に設定
      } else {
        this._hideImage();
        this.previewImage.dataset.clickable = 'false'; // クリック不可に設定
      }

    } catch(e) {
      console.log("showSuccessPreview: NG", e);
      this._hideImage();
      this.previewImage.dataset.clickable = 'false'; // クリック不可に設定
    }
  }
  
  /**
   * 途中経過イベント
   */
  _showProgressPreview(detail){
    this.images = []; // 画像リストをリセット

    try {
      // 既存のBlob URLがあれば破棄
      if (this.progressPreviewBlobUrl) {
        URL.revokeObjectURL(this.progressPreviewBlobUrl);
      }
      // 新しいBlob URLを作成して設定
      this.progressPreviewBlobUrl = URL.createObjectURL(detail);
      this._showImage(this.progressPreviewBlobUrl);

      // プログレス中はクリック不可にする
      this.previewImage.dataset.clickable = 'false'; // クリック不可に設定

    } catch(e) {
      this._hideImage();
    }
  }

  /**
   * 画像を表示
   * @param {*} src 
   */
  _showImage(src){
    this.previewImage.src = src;
    // this.previewImage.style.opacity = 1;
    this.previewImage.style.visibility = "visible";
    this._titleElement.style.visibility = "hidden";
  }

  /**
   * 画像を非表示
   */
  _hideImage(){
    this.previewImage.src = "";
    // this.previewImage.style.opacity = 0;
    this.previewImage.style.visibility = "hidden";
    this._titleElement.style.visibility = "visible";
  }
  
  /**
   * プレビュー画像クリックイベント
   */
  _handlePreviewClick() {
    // クリック可能状態か、画像リストがあるかチェック
    if (this.previewImage.dataset.clickable !== 'true' || !this.images || this.images.length === 0) {
      console.warn("Preview image is not clickable or no images available.");
      return;
    }
    // D2Lightbox.openLightbox は URL の配列を期待する
    D2Lightbox.openLightbox(this.images, 0);
  }

  /**
   * プレビュー作成
   */
  _createPreview() {
    const wrapper = document.createElement('div');
    wrapper.style.position = "relative";
    this.floatContainer.addContent(wrapper);

    const title = document.createElement('span');
    title.textContent = "D2 Progress Preview";
    title.style.position = "absolute";
    title.style.bottom = 0;
    title.style.opacity = 0.2;
    title.style.fontSize = "0.8em";
    title.style.textAlign = "center";
    wrapper.appendChild(title);
    this._titleElement = title;

    const image = new Image();
    image.style.width = '150px';
    image.style.height = '150px';
    image.style.objectFit = 'contain';
    // image.style.opacity = 0;
    image.style.visibility = "hidden";
    image.style.position = "relative";
    image.dataset.clickable = 'false'; // 初期状態はクリック不可に設定
    image.classList.add("d2-progress-preview-image");
    wrapper.appendChild(image);
    this.previewImage = image;

    // クリックイベントリスナーを設定
    image.addEventListener("click", this._boundHandlePreviewClick);
  }
}


(function () {
  const progressPreview = new D2_ProgressPreview();

  app.ui.settings.addSetting({
    id: "D2.ProgressPreview.Visible",
    name: "Show progress preview",
    type: "boolean",
    defaultValue: true,
    onChange(value) {
      progressPreview.changeVisible(value);
    },
  });
})();
