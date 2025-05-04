import { app } from "/scripts/app.js";
import { findWidgetByName } from "./modules/utils.js";


class D2FileUploader {
    imageListWidget = undefined;
    imageCountWidget = undefined;
    statusWidget = undefined;

    init(imageListWidget, statusWidget, imageCountWidget) {
        this.imageListWidget = imageListWidget;
        this.statusWidget = statusWidget;
        this.imageCountWidget = imageCountWidget;
        // this.updateImageCount(); // 初期値を設定

        const textarea = imageListWidget.inputEl;

        // イベントリスナーを設定
        textarea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            textarea.classList.add('dragover');
            textarea.style.opacity = 0.5;
        });
        
        textarea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            textarea.classList.remove('dragover');
            textarea.style.opacity = 1;
        });
        
        textarea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            textarea.classList.remove('dragover');
            textarea.style.opacity = 1;
            
            const files = e.dataTransfer.files;
            
            if (files.length > 0) {
                // 画像ファイルのみをフィルタリング
                const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
                
                if (imageFiles.length > 0) {
                    this.uploadFiles(imageFiles);
                } else {
                    // 画像ファイルのみサポートしてるエラー
                    this.statusWidget.setValue("Only image files are supported");
                }
            }
        });

    }

    // ファイルをアップロードする関数
    uploadFiles(files) {
        const formData = new FormData();
        
        for (let i = 0; i < files.length; i++) {
            formData.append('file' + i, files[i]);
        }

        this.statusWidget.setValue("Uploading...");

        fetch('/D2/network/image/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // レスポンスが OK でない場合、エラーとして処理
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, message: ${text}`);
                });
            }
            // Content-Type が application/json であることを期待
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                 // JSON 形式でない場合、テキストとして処理しエラーを投げる
                 return response.text().then(text => {
                    throw new Error(`Expected JSON, but received ${contentType}. Response body: ${text}`);
                });
            }
            return response.json(); // JSON としてパース
        })
        .then(data => {
            // 成功した場合の処理 (例: ステータス更新)
            this.statusWidget.setValue(data.message || 'Files uploaded successfully'); // サーバーからのメッセージがあれば表示
            
            let outputText = this.imageListWidget.value || "";

            data.files.forEach(file => {
                outputText = file.path + "\n" + outputText;
            });
            
            this.imageListWidget.value = outputText;
            this.updateImageCount();
            
        })
        .catch(error => {
            console.error("Upload error occurred:"); // エラーログを明確化
            console.error(error); // エラーオブジェクト全体を出力
            // エラーメッセージを statusWidget に表示
            // Error オブジェクトに message プロパティがあることを確認
            const errorMessage = error instanceof Error ? error.message : String(error);
            this.statusWidget.setValue('Upload failed: ' + errorMessage);
        });
    }

    // 画像の行数をカウントしてウィジェットを更新する関数
    updateImageCount() {
        const outputText = this.imageListWidget.value || "";
        // 空行は対象外として行数をカウント
        const image_count = outputText.split("\n").filter(line => line.trim() !== "").length;
        this.imageCountWidget.setValue(image_count);
    }
}


app.registerExtension({
    name: "Comfy.D2.D2_UploadImage",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 XY Upload Image") return;

        // ファイルアップロードクラスのインスタンスを作成
        const fileUploader = new D2FileUploader();

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const statusWidget =  findWidgetByName(this, "status");
            const imageListWidget = findWidgetByName(this, "image_list");
            const imageCountWidget = findWidgetByName(this, "image_count");
            imageCountWidget.textTemplate = "Image count: <%value%>"

            fileUploader.init(imageListWidget, statusWidget, imageCountWidget);


            return r;
        };

        /**
         * ノード実行時
         */
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = async function (message) {
            onExecuted?.apply(this, arguments);

            const imageCount = message["image_count"][0];
            const imageCountWidget = findWidgetByName(this, "image_count");
            imageCountWidget.setValue(imageCount);
        };
    },


});
