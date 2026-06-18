/**
 * ボタンを並べた小さいフロートウィンドウのクラス
 */

import { app } from "../../scripts/app.js";
import { setCookie, getCookie, loadCssFile } from "./modules/utils.js";

const CSS_CLASS_BUTTON_BASE =
    'inline-flex items-center justify-center cursor-pointer touch-manipulation appearance-none border-none text-sm font-inter transition-colors h-8 rounded-lg px-4 font-light';
const CSS_CLSSS_BUTTON_PRIMARY = 'text-base-foreground bg-primary-background hover:bg-primary-background-hover';
const CSS_CLSSS_BUTTON_SECONDARY = 'text-secondary-foreground bg-secondary-background hover:bg-secondary-background-hover';

// dock から離脱する移動量しきい値（px）
const DOCK_BREAKAWAY_THRESHOLD = 6;


class D2_FloatContainer {
    static CSS_FILEPATH = "/D2/assets/css/D2_FloatContainer.css?3";

    container = undefined;
    frame = undefined;
    body = undefined;
    cookieNameBase = "";

    // ドック機能
    enableDock = false;
    mode = "float";        // "float" | "dock"
    visible = true;
    dockGroup = null;      // アクションバーへ挿入する ComfyButtonGroup（ドック先＆ドロップ枠を兼ねる）

    /**
     * @param {string} cookieNameBase cookie キーの接頭辞
     * @param {number} default_left 初期位置 X
     * @param {number} default_top 初期位置 Y
     * @param {{enableDock?: boolean}} options enableDock: true でアクションバー収納を有効化
     */
    constructor(cookieNameBase, default_left = 50, default_top = 50, options = {}) {
        this.cookieNameBase = cookieNameBase;
        this.enableDock = options.enableDock === true;
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

        // ドック状態の復元（遅延）
        if (this.enableDock) {
            this._restoreDockState();
        }
    }

    /**
     * 内容物追加
     * @param {HTMLElement} button
     */
    addContent(button) {
        this.body.appendChild(button);
    }

    /**
     * 内容物全削除
     */
    removeAllContent() {
        this.body.innerHTML = "";
    }

    /**
     * 表示切り替え
     */
    changeVisible(bool) {
        this.visible = bool;
        this._applyVisible();
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

        this.frame = document.createElement("div");
        this.frame.classList.add("p-panel-content", "flex", "flex-nowrap", "items-center", "d2-float-container__frame");
        this.container.appendChild(this.frame);

        const dragHandle = document.createElement("span");
        dragHandle.classList.add("drag-handle", "cursor-grab", "w-3", "mr-2", "d2-float-container__drag-handle");
        this.frame.appendChild(dragHandle);

        this.body = document.createElement("div");
        this.body.classList.add("flex", "flex-nowrap", "items-center", "d2-float-container__body");
        this.frame.appendChild(this.body);

        // ドラッグ設定
        this._dragSetting(dragHandle, this.container);
    }

    /**
     * 現在の visible / mode に応じて表示状態を適用する
     */
    _applyVisible() {
        const bool = this.visible;
        this.frame.style.display = bool ? "flex" : "none";
        if (this.mode === "float") {
            // float 時はラッパパネルごと表示/非表示
            this.container.style.display = bool ? "block" : "none";
        } else {
            // dock 時は frame が container 外にあるため、空のラッパは常に隠す
            this.container.style.display = "none";
        }
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
     * ドック状態をcookieに記録
     */
    _saveMode() {
        setCookie(`${this.cookieNameBase}_dock`, this.mode === "dock");
    }

    /**
     * 保存されたドック状態を取得
     */
    _getSavedDock() {
        return getCookie(`${this.cookieNameBase}_dock`) === true;
    }

    ///////////////////////////////////////////////
    // dock 関連
    ///////////////////////////////////////////////
    /**
     * ドック先＆ドロップ枠用の ComfyButtonGroup をアクションバーへ挿入（初回のみ）
     * @returns {object|null}
     */
    _createDockGroup() {
        const ButtonGroup = window.comfyAPI?.buttonGroup?.ComfyButtonGroup;
        const settingsGroup = app.menu?.settingsGroup;
        if (!ButtonGroup || !settingsGroup?.element) return null;

        const group = new ButtonGroup();
        group.element.classList.add("d2-dock-group");
        settingsGroup.element.before(group.element);
        this.dockGroup = group;
        return group;
    }

    /**
     * ドック可能か（毎回評価）。利用不可なら false。
     * 利用可能なら dockGroup を遅延生成する。
     */
    _canDock() {
        if (!this.enableDock) return false;
        const ButtonGroup = window.comfyAPI?.buttonGroup?.ComfyButtonGroup;
        const settingsGroup = app.menu?.settingsGroup;
        if (!ButtonGroup || !settingsGroup?.element) return false;
        if (!this.dockGroup) {
            this._createDockGroup();
        }
        return !!this.dockGroup;
    }

    /**
     * ドロップ枠を表示（border-dashed でアクションバーが開く）
     */
    _showDropTarget() {
        if (!this.dockGroup) return;
        this.dockGroup.element.classList.add("border-dashed", "d2-dock-drop-target");
    }

    /**
     * ドロップ枠を畳む
     */
    _hideDropTarget() {
        if (!this.dockGroup) return;
        this.dockGroup.element.classList.remove("border-dashed", "d2-dock-drop-target", "d2-dock-drop-ready");
    }

    /**
     * ドロップ可能状態のハイライト切り替え
     */
    _highlightDropTarget(on) {
        if (!this.dockGroup) return;
        this.dockGroup.element.classList.toggle("d2-dock-drop-ready", !!on);
    }

    /**
     * 表示中のドロップ枠の矩形を返す（未表示/サイズ0なら null）
     */
    _getDropTargetRect() {
        if (!this.dockGroup) return null;
        const rect = this.dockGroup.element.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return null;
        return rect;
    }

    /**
     * float ⇔ dock の切り替え
     * @param {boolean} bool true で dock、false で float
     */
    setDock(bool) {
        if (bool) {
            if (!this._canDock()) return;
            this.dockGroup.element.appendChild(this.frame);
            this.dockGroup.element.classList.add("d2-dock-active");
            this._hideDropTarget();
            this.mode = "dock";
        } else {
            this.container.appendChild(this.frame);
            if (this.dockGroup) {
                this.dockGroup.element.classList.remove("d2-dock-active");
            }
            this.mode = "float";
            // 位置を復元
            const pos = this._getPosition(50, 50);
            this.container.style.left = pos[0] + "px";
            this.container.style.top = pos[1] + "px";
            this.resizeSetting();
        }
        this._applyVisible();
        this._saveMode();
    }

    /**
     * 起動時のドック状態復元（app.menu の生成を待つ）
     */
    _restoreDockState() {
        if (!this._getSavedDock()) return;
        let tries = 0;
        const tryDock = () => {
            if (this._canDock()) {
                this.setDock(true);
                return;
            }
            if (tries++ < 60) {
                setTimeout(tryDock, 100);
            }
        };
        tryDock();
    }

    /**
     * ドラッグ設定
     */
    _dragSetting(handle, container) {
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;
        let dropReady = false;       // float ドラッグ中: カーソルが枠内
        let brokeAway = false;       // dock ドラッグ中: しきい値を超えて離脱済み

        // マウスダウンイベントリスナー
        handle.addEventListener("mousedown", (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = container.offsetLeft;
            initialTop = container.offsetTop;
            dropReady = false;
            brokeAway = false;

            // float 時はドロップ枠を表示
            if (this.mode === "float" && this._canDock()) {
                this._showDropTarget();
            }

            // テキスト選択を防止
            e.preventDefault();
        });

        // マウスムーブイベントリスナー
        document.addEventListener("mousemove", (e) => {
            if (!isDragging) return;

            // dock 中: しきい値を超えるまでは動かさない
            if (this.mode === "dock") {
                const dist = Math.abs(e.clientX - startX) + Math.abs(e.clientY - startY);
                if (!brokeAway) {
                    if (dist < DOCK_BREAKAWAY_THRESHOLD) return;
                    brokeAway = true;
                    // float へ離脱し、カーソル位置へ移してドラッグ継続
                    this.setDock(false);
                    initialLeft = e.clientX - 10;
                    initialTop = e.clientY - 10;
                    startX = e.clientX;
                    startY = e.clientY;
                }
            }

            // float 移動
            const x = e.clientX - startX + initialLeft;
            const y = e.clientY - startY + initialTop;
            container.style.left = `${x}px`;
            container.style.top = `${y}px`;
            this._savePosition(x, y);

            // ドロップ枠の当たり判定（float 時のみ）
            if (this.mode === "float" && this._canDock()) {
                const rect = this._getDropTargetRect();
                dropReady = !!(rect &&
                    e.clientX >= rect.left && e.clientX <= rect.right &&
                    e.clientY >= rect.top && e.clientY <= rect.bottom);
                this._highlightDropTarget(dropReady);
            }
        });

        // マウスアップイベントリスナー
        document.addEventListener("mouseup", () => {
            if (!isDragging) return;
            isDragging = false;

            if (this.mode === "float" && this._canDock()) {
                if (dropReady) {
                    this.setDock(true);
                } else {
                    this._hideDropTarget();
                }
            }
            dropReady = false;
            brokeAway = false;
        });

        // マウスリーブイベントリスナー（ブラウザ外にマウスが出た場合）
        document.addEventListener("mouseleave", () => {
            if (!isDragging) return;
            isDragging = false;
            this._hideDropTarget();
            dropReady = false;
            brokeAway = false;
        });
    }

    /**
     * ウィンドウリサイズ対策
     */
    resizeSetting() {
        // dock 時は位置調整不要
        if (this.mode === "dock") return;

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

export { D2_FloatContainer, CSS_CLASS_BUTTON_BASE, CSS_CLSSS_BUTTON_PRIMARY, CSS_CLSSS_BUTTON_SECONDARY }
