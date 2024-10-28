/**
 * ボタンを並べた小さいフロートウィンドウのクラス
 */

import { setCookie, getCookie, loadCssFile } from "./utils.js";


class D2_FloatContainer {
    static CSS_FILEPATH = "./extensions/D2-nodes-ComfyUI/css/D2_FloatContainer.css";

    container = undefined;
    buttonContainer = undefined;
    cookieNameBase = "";

    constructor(cookieNameBase, default_left = 50, default_top = 50) {
        this.cookieNameBase = cookieNameBase;
        loadCssFile(D2_FloatContainer.CSS_FILEPATH);
        this._createContainer();

        // 初期位置
        const pos = this._getPosition(default_left, default_top);
        this.container.style.left = pos[0] + "px";
        this.container.style.top = pos[1] + "px";

        // ウィンドウリサイズ対策
        window.addEventListener("resize", () => {
            this.resizeSetting();
        });
        this.resizeSetting();
    }

    /**
     * ボタン追加
     * @param {HTMLElement} button 
     */
    addButton(button) {
        this.buttonContainer.appendChild(button);
    }

    /**
     * ボタン全削除
     */
    removeButtons() {
        this.buttonContainer.innerHTML = "";
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
        this.container.classList.add("p-panel", "d2-float-container");
        document.querySelector("body").appendChild(this.container);

        const content = document.createElement("div");
        content.classList.add("p-panel-content", "flex", "flex-nowrap", "items-center", "d2-float-container__content");
        this.container.appendChild(content);

        const dragHandle = document.createElement("span");
        dragHandle.classList.add("drag-handle", "cursor-move", "mr-2");
        content.appendChild(dragHandle);

        this.buttonContainer = document.createElement("div");
        this.buttonContainer.classList.add("flex", "flex-nowrap", "items-center", "d2-float-container__button-container");
        content.appendChild(this.buttonContainer);

        // ドラッグ設定
        this._dragSetting(dragHandle, this.container);
    }

    /**
     * 座標をcookieに記録
     */
    _savePosition(x, y) {
        const cookieName = `${this.cookieNameBase}_pos`;
        const cookieValue = [x, y];
        setCookie(cookieName, cookieValue);
    }

    /**
     * 座標をcookieから取得
     */
    _getPosition(default_left, default_top) {
        const cookieName = `${this.cookieNameBase}_pos`;
        const cookieValue = getCookie(cookieName);
        return cookieValue !== undefined ? cookieValue : [default_left, default_top];
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

            this._savePosition(x, y);
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
            container.style.left = "0px";
        }

        // 下端の調整
        if (rect.bottom > viewportHeight) {
            const newTop = Math.max(0, viewportHeight - rect.height);
            container.style.top = `${newTop}px`;
        } else if (rect.top < 0) {
            container.style.top = "0px";
        }
    }
}

export { D2_FloatContainer }
