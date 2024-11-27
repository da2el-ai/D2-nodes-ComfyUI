
import { loadCssFile } from "./utils.js";

const CSS_FILEPATH = "./extensions/D2-nodes-ComfyUI/css/D2_Lightbox.css";
const IMAGE_URL = '/api/view?filename={filename}&subfolder=&type=temp&rand={random}';

loadCssFile(CSS_FILEPATH);

/**
 * エレメント作成
 */
const _createLightboxBase = () => {
    const container = document.createElement('div');
    container.classList.add('d2-lightbox');
    // フォーカス可能にする
    container.setAttribute('tabindex', '-1');
    document.querySelector('body').appendChild(container);

    const bg = document.createElement('div');
    bg.classList.add('d2-lightbox__bg');
    container.appendChild(bg);

    const content = document.createElement('div');
    content.classList.add('d2-lightbox__content');
    container.appendChild(content);

    const galleryContainer = document.createElement('div');
    galleryContainer.classList.add('d2-lightbox__gallery');
    content.appendChild(galleryContainer);

    const galleryImage = document.createElement('img');
    galleryImage.classList.add('d2-lightbox__gallery-image');
    galleryContainer.appendChild(galleryImage);

    const listContainer = document.createElement('div');
    listContainer.classList.add('d2-lightbox__list');
    content.appendChild(listContainer);

    return {
        container, galleryContainer, galleryImage, listContainer
    }
}


/**
 * 
 */
class D2Lightbox{

    constructor(){
        const elements = _createLightboxBase();
        this.container = elements.container;
        this.galleryContainer = elements.galleryContainer;
        this.galleryImage = elements.galleryImage;
        this.listContainer = elements.listContainer;
        this.nowIndex = 0;
        this.images = [];
        this.resizeTimer;

        // 背景クリックで閉じる
        this.galleryContainer.addEventListener('click', ()=>{ this.closeLightbox(); });

        // thisをバインドしてコールバック内でも正しくthisが参照できるようにする
        this._onKeyDown = this._onKeyDown.bind(this);
    }

    openLightbox(imageObjects, imageIndex = 0){
        this._removeListImages();
        this._addListimageObjects(imageObjects);
        this._clickListImage(imageIndex);
        this.container.style.display = 'block';

        // Lightboxを開いた時に自動でフォーカスを設定
        this.container.focus();

        // リサイズイベントリスナーを追加
        // 既存のリサイズイベントリスナーを削除（重複防止）
        window.removeEventListener('resize', this._handleResize);
        window.addEventListener('resize', this._handleResize);
        // キーボードイベントリスナー
        document.removeEventListener('keydown', this._onKeyDown);
        document.addEventListener('keydown', this._onKeyDown);
    }

    closeLightbox(){
        this.container.style.display = 'none';
        this.galleryImage.style.display = 'none';
        this._removeListImages();

        // リサイズイベントリスナーを削除
        window.removeEventListener('resize', this._handleResize, this);
        document.removeEventListener('keydown', this._onKeyDown);
    }

    /**
     * リスト画像をクリック
     * @param {int} targetImg 
     */
    _clickListImage(index){
        this.images[this.nowIndex].dataset.active = 'false';

        const targetImg = this.images[index];
        targetImg.dataset.active = 'true';
        this.galleryImage.src = targetImg.src;
        this.galleryImage.style.display = 'inline';
        this.galleryImage.style.width = 'auto';
        this.galleryImage.style.height = 'auto';
        this.nowIndex = index;

        this.galleryImage.decode().then(()=>{
            this._resetGalleryPosition();
        });
}

    /**
     * 画像サイズと位置の調整
     */
    _resetGalleryPosition(){
        // コンテナサイズ取得。高さはリストを除外した高さ
        const containerW = this.galleryContainer.clientWidth;
        const containerH = this.galleryContainer.clientHeight - 100;
        const imgW = this.galleryImage.width;
        const imgH = this.galleryImage.height;
        const aspect = imgW / imgH;
        
        let newWidth, newHeight;

        // コンテナに合わせてサイズを計算
        if (containerW / containerH > aspect) {
            // コンテナの方が横長の場合、高さに合わせる
            newHeight = containerH;
            newWidth = containerH * aspect;
        } else {
            // コンテナの方が縦長の場合、幅に合わせる
            newWidth = containerW;
            newHeight = containerW / aspect;
        }
    
        // 画像の新しいサイズを設定
        this.galleryImage.style.width = `${newWidth}px`;
        this.galleryImage.style.height = `${newHeight}px`;
    
        // 中央配置のための位置計算
        const left = (containerW - newWidth) / 2;
        const top = (containerH - newHeight) / 2;
    
        // 位置を設定
        this.galleryImage.style.left = `${left}px`;
        this.galleryImage.style.top = `${top}px`;    }

    /**
     * リスト画像を追加
     * @param {filename:string} imageObjects 
     */
    _addListimageObjects(imageObjects){
        imageObjects.forEach((imgObj, index) => {
            let url = IMAGE_URL.replace('{filename}', imgObj.filename);
            url = url.replace('{random}', Math.random());

            const img = document.createElement('img');
            img.classList.add('d2-lightbox__list-image');
            img.src = url;
            img.index = index;
            img.dataset.active = 'false';
            img.addEventListener('click', (ev)=>{
                this._clickListImage(ev.target.index);
            })
            this.listContainer.appendChild(img);
            this.images.push(img);
        });
    }

    /**
     * 既存のリスト画像を削除する
     */
    _removeListImages(){
        this.images.forEach(img => {
            this.listContainer.removeChild(img);
        });
        this.images = [];
    }

    // デバウンス処理付きのリサイズハンドラ
    _handleResize = () => {
        clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout(() => {
            this._resetGalleryPosition();
        }, 200); // 200ms後に実行
    };

    _onKeyDown = (ev) => {
        if(ev.key === 'Escape'){
            this.closeLightbox();
        }
    }
}

export {D2Lightbox}
