import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { D2_FloatContainer } from "./D2_FloatContainer.js";
import { D2Lightbox } from "./modules/util_lightbox.js";
import { sleep } from "./modules/utils.js";



/**
 * Progress Preview を作るクラス
 */
class D2_ProgressPreview {
  floatContainer = undefined;
  progressPreviewBlobUrl = undefined;
  previewImage = undefined;
  _boundShowProgressPreview = null;
  _boundShowSuccessPreview = null;
  _lastPromptId = undefined;

  constructor() {
    // イベントハンドラをバインド
    this._boundShowProgressPreview = ({detail}) => this._showProgressPreview(detail);
    this._boundShowSuccessPreview = ({detail}) => this._showSuccessPreview(detail);

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

    if(!detail.prompt_id) return;
    if(this._lastPromptId === detail.prompt_id) return;

    this._lastPromptId = detail.prompt_id;
    await sleep(200);

    const images = [];

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
              const preview = image.type === "temp" ? '&type=temp' : '';
              const imageUrl = api.apiURL(`/view?filename=${image.filename}${preview}`);
              console.log(`Adding image URL: ${imageUrl}`);
              images.push(imageUrl);
            }
          }
        }
      }

      this.previewImage.src = images[0];
      this.previewImage.style.opacity = 1;

      const lightBox = new D2Lightbox();

      previewBtnWidget.callback = () => {
        lightBox.openLightbox(images, 0);
      };

    } catch(e) {
      console.log("showSuccessPreview: NG", e);
      this.previewImage.style.opacity = 0;
    }
  }
  
  /**
   * 途中経過イベント
   */
  _showProgressPreview(detail){
    try {
      if (this.progressPreviewBlobUrl) {
        URL.revokeObjectURL(this.progressPreviewBlobUrl);
      }
      this.progressPreviewBlobUrl = URL.createObjectURL(detail);
      this.previewImage.src = this.progressPreviewBlobUrl;
      this.previewImage.style.opacity = 1;
    } catch(e) {
      this.previewImage.style.opacity = 0;
    }
  }

  /**
   * プレビュー作成
   */
  _createPreview() {
    const wrapper = document.createElement('div');
    wrapper.style.position = "relative";

    const title = document.createElement('span');
    title.textContent = "D2 Progress Preview";
    title.style.position = "absolute";
    title.style.bottom = 0;
    title.style.opacity = 0.2;
    title.style.fontSize = "0.8em";
    wrapper.appendChild(title);

    const image = new Image();
    image.style.width = '150px';
    image.style.height = '150px';
    image.style.objectFit = 'contain';
    image.style.opacity = 0;
    image.style.position = "relative";
    wrapper.appendChild(image);

    this.floatContainer.addContent(wrapper);
    this.previewImage = image;
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
