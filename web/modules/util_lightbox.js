
import { loadCssFile } from "./utils.js";

const CSS_FILEPATH = "/D2/assets/css/D2_Lightbox.css";
const IMAGE_URL = '/api/view?filename={filename}&subfolder=&type=temp&rand={random}';

loadCssFile(CSS_FILEPATH);

/**
 * エレメント作成
 */
/**
 * ライトボックスの基本要素を保持する静的プロパティ
 */
let lightboxElements = null;
let nowIndex = 0;
let images = [];
let resizeTimer;

/**
 * エレメント作成と初期化
 */
const _initLightboxBase = () => {
    if (lightboxElements) {
        return lightboxElements; // 既に初期化済みなら既存の要素を返す
    }

    const container = document.createElement('div');
    container.classList.add('d2-lightbox');
    container.style.display = 'none'; // 初期状態は非表示
    // フォーカス可能にする
    container.setAttribute('tabindex', '-1'); // フォーカス可能にする
    document.body.appendChild(container);

    const bg = document.createElement('div');
    bg.classList.add('d2-lightbox__bg'); // 背景クリックで閉じるイベントはここに移動するかも
    container.appendChild(bg);
    bg.addEventListener('click', D2Lightbox.closeLightbox); // 背景クリックで閉じる

    const content = document.createElement('div');
    content.classList.add('d2-lightbox__content');
    container.appendChild(content);

    const galleryContainer = document.createElement('div');
    galleryContainer.classList.add('d2-lightbox__gallery');
    content.appendChild(galleryContainer);
    // galleryContainer のクリックイベントは削除（背景で閉じるため）

    const galleryImage = document.createElement('img');
    galleryImage.classList.add('d2-lightbox__gallery-image');
    galleryImage.style.display = 'none'; // 初期状態は非表示
    galleryContainer.appendChild(galleryImage);

    const listContainer = document.createElement('div');
    listContainer.classList.add('d2-lightbox__list');
    content.appendChild(listContainer);

    // 生成した要素を静的プロパティに格納
    lightboxElements = {
        container, galleryContainer, galleryImage, listContainer
    };
    return lightboxElements;
}


/**
 * 静的メソッドのみを持つライトボックスクラス
 */
class D2Lightbox {

    // constructor は不要

    static openLightbox(imageObjects, imageIndex = 0) {
        // 初回呼び出し時に要素を初期化
        if (!lightboxElements) {
            _initLightboxBase();
        }

        D2Lightbox._removeListImages();
        D2Lightbox._addListimageObjects(imageObjects);
        D2Lightbox._clickListImage(imageIndex);
        lightboxElements.container.style.display = 'block';

        // Lightboxを開いた時に自動でフォーカスを設定
        lightboxElements.container.focus();

        // リサイズイベントリスナーを追加（重複防止のため削除してから追加）
        window.removeEventListener('resize', D2Lightbox._handleResize);
        window.addEventListener('resize', D2Lightbox._handleResize);
        // キーボードイベントリスナーを追加（重複防止のため削除してから追加）
        document.removeEventListener('keydown', D2Lightbox._onKeyDown);
        document.addEventListener('keydown', D2Lightbox._onKeyDown);
    }

    static closeLightbox() {
        if (!lightboxElements) return; // 要素がなければ何もしない

        lightboxElements.container.style.display = 'none';
        lightboxElements.galleryImage.style.display = 'none';
        D2Lightbox._removeListImages();

        // イベントリスナーを削除
        window.removeEventListener('resize', D2Lightbox._handleResize);
        document.removeEventListener('keydown', D2Lightbox._onKeyDown);
    }

    /**
     * リスト画像をクリック
     * @param {int} index
     */
    static _clickListImage(index) {
        if (!lightboxElements || !images || images.length === 0) return;

        // 前の画像を非アクティブに
        if (images[nowIndex]) {
            images[nowIndex].dataset.active = 'false';
        }

        const targetImg = images[index];
        if (!targetImg) return; // 対象画像がなければ終了

        targetImg.dataset.active = 'true';
        lightboxElements.galleryImage.src = targetImg.src;
        lightboxElements.galleryImage.style.display = 'inline';
        lightboxElements.galleryImage.style.width = 'auto';
        lightboxElements.galleryImage.style.height = 'auto';
        nowIndex = index;

        // 画像読み込み後にリサイズ処理
        lightboxElements.galleryImage.decode().then(() => {
            D2Lightbox._resetGalleryPosition();
        }).catch(error => {
            console.error("Error decoding image:", error);
            // エラー時もリサイズを試みる（表示されているかもしれないため）
            D2Lightbox._resetGalleryPosition();
        });
    }

    /**
     * 画像サイズと位置の調整
     */
    static _resetGalleryPosition() {
        if (!lightboxElements || !lightboxElements.galleryImage.src || lightboxElements.galleryImage.style.display === 'none') return;

        // コンテナサイズ取得。高さはリストを除外した高さ
        const containerW = lightboxElements.galleryContainer.clientWidth;
        // リストの高さを取得（存在しない場合や非表示の場合は0）
        const listH = lightboxElements.listContainer.offsetHeight || 0;
        const containerH = lightboxElements.galleryContainer.clientHeight - listH; // リストの高さを引く

        // 画像の自然なサイズを取得
        const imgW = lightboxElements.galleryImage.naturalWidth;
        const imgH = lightboxElements.galleryImage.naturalHeight;

        if (containerW <= 0 || containerH <= 0 || imgW <= 0 || imgH <= 0) {
            // 無効なサイズの場合は何もしない
            return;
        }

        const aspect = imgW / imgH;
        let newWidth, newHeight;

        // コンテナに合わせてサイズを計算
        if (containerW / containerH > aspect) {
            // コンテナの方が横長の場合、高さに合わせる
            newHeight = Math.min(imgH, containerH); // 元画像より大きくしない
            newWidth = newHeight * aspect;
            if (newWidth > containerW) { // 幅がはみ出る場合は幅に合わせる
                newWidth = containerW;
                newHeight = newWidth / aspect;
            }
        } else {
            // コンテナの方が縦長またはアスペクト比が同じ場合、幅に合わせる
            newWidth = Math.min(imgW, containerW); // 元画像より大きくしない
            newHeight = newWidth / aspect;
             if (newHeight > containerH) { // 高さがはみ出る場合は高さに合わせる
                newHeight = containerH;
                newWidth = newHeight * aspect;
            }
        }

        // 画像の新しいサイズを設定
        lightboxElements.galleryImage.style.width = `${newWidth}px`;
        lightboxElements.galleryImage.style.height = `${newHeight}px`;

        // 中央配置のための位置計算
        const left = (containerW - newWidth) / 2;
        // topの位置はリストの高さを考慮しないgalleryContainer基準で計算
        const top = (containerH - newHeight) / 2;

        // 位置を設定
        lightboxElements.galleryImage.style.left = `${left}px`;
        // topはリストの高さを考慮しない位置
        lightboxElements.galleryImage.style.top = `${top}px`;
    }


    /**
     * リスト画像を追加
     * @param {Array<{filename: string}>} imageObjects
     */
    static _addListimageObjects(imageObjects) {
        if (!lightboxElements) return;
        images = []; // リストをクリア
        lightboxElements.listContainer.innerHTML = ''; // コンテナをクリア

        imageObjects.forEach((imgObj, index) => {
            let url = IMAGE_URL.replace('{filename}', imgObj.filename);
            url = url.replace('{random}', Math.random());

            const img = document.createElement('img');
            img.classList.add('d2-lightbox__list-image');
            img.src = url;
            // img.index = index; // datasetで管理する方が安全
            img.dataset.index = index;
            img.dataset.active = 'false';
            img.addEventListener('click', (ev) => {
                // クリックされた画像のインデックスを取得
                const clickedIndex = parseInt(ev.target.dataset.index, 10);
                D2Lightbox._clickListImage(clickedIndex);
            });
            lightboxElements.listContainer.appendChild(img);
            images.push(img); // 静的プロパティの配列に追加
        });
    }

    /**
     * 既存のリスト画像を削除する
     */
    static _removeListImages() {
        if (!lightboxElements) return;
        images.forEach(img => {
            if (img.parentNode === lightboxElements.listContainer) {
                lightboxElements.listContainer.removeChild(img);
            }
        });
        images = []; // 静的プロパティの配列をクリア
        nowIndex = 0; // インデックスもリセット
    }

    // デバウンス処理付きのリサイズハンドラ
    static _handleResize = () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            D2Lightbox._resetGalleryPosition();
        }, 200); // 200ms後に実行
    };

    /**
     * ライトボックスが表示されているかどうかを返す
     * @returns {boolean}
     */
    static _isLightboxVisible() {
        return lightboxElements && lightboxElements.container.style.display !== 'none';
    }

    // キーダウンイベントハンドラ
    static _onKeyDown = (ev) => {
        // ライトボックスが表示されていない場合は何もしない
        if (!D2Lightbox._isLightboxVisible()) {
            return;
        }

        let handled = false;
        if (ev.key === 'Escape') {
            D2Lightbox.closeLightbox();
            handled = true;
        } else if (ev.key === 'ArrowLeft') {
            // 左矢印キー: 前の画像へ
            const prevIndex = (nowIndex - 1 + images.length) % images.length;
            D2Lightbox._clickListImage(prevIndex);
            handled = true;
        } else if (ev.key === 'ArrowRight') {
            // 右矢印キー: 次の画像へ
            const nextIndex = (nowIndex + 1) % images.length;
            D2Lightbox._clickListImage(nextIndex);
            handled = true;
        }

        // ライトボックスでキーが処理された場合、イベントの伝播とデフォルト動作を停止
        if (handled) {
            ev.preventDefault();
            ev.stopPropagation();
        }
    }
}

export { D2Lightbox };
