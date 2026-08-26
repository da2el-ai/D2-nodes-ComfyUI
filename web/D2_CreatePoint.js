import { app } from "/scripts/app.js";
import { api } from "../../scripts/api.js";
import { findWidgetByName, findOutputByName, getReadOnlyWidgetBase } from "./modules/utils.js";

const NODE_TITLE = "D2 Create Point";

const CANVAS_MARGIN = 10;
const CANVAS_MAX_HEIGHT = 1280;
const MIN_CANVAS_HEIGHT = 64;
// computeSize が引数なしで呼ばれ、かつノード幅もまだ無いときの保険
const DEFAULT_NODE_WIDTH = 240;
const MARKER_RADIUS = 10;
const GRAB_RADIUS = 16;
// 座標 JSON の小数桁。6桁なら最大解像度 16384px でも 0.02px 未満の誤差に収まる
const COORD_DIGITS = 6;

const MODE_ABSOLUTE = "absolute";


/**
 * マーカーの既定位置（相対値）。左から等間隔・縦は中央。
 * nodes/modules/marker_util.py の default_marker_position と同じ式にすること。
 * ここがズレると、実行するまで気づかない座標の食い違いになる。
 */
const defaultMarkerPosition = (index, count) => ({ x: (index + 1) / (count + 1), y: 0.5 });

/**
 * 0.0〜1.0 に収める。数値として扱えなければ null
 */
const clamp01 = (value) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return null;
    return Math.min(1, Math.max(0, num));
};

/**
 * ウィジェットの数値を取得する
 */
const getNumber = (node, name, fallback) => {
    const widget = findWidgetByName(node, name);
    const num = Number(widget?.value);
    return Number.isFinite(num) ? num : fallback;
};

/**
 * マーカー1件を正規化する。取り出せなければ既定位置
 */
const normalizeMarker = (item, index, count) => {
    if (item === null || typeof item !== "object") return defaultMarkerPosition(index, count);

    const x = clamp01(item.x);
    const y = clamp01(item.y);
    if (x === null || y === null) return defaultMarkerPosition(index, count);

    return { x, y };
};

/**
 * JSON をパースして配列を返す。壊れていれば null
 */
const tryParseMarkers = (markersJson) => {
    try {
        const parsed = JSON.parse(markersJson);
        return Array.isArray(parsed) ? parsed : null;
    } catch (e) {
        return null;
    }
};

/**
 * パース済み配列を正規化する。
 * count に満たない分は既定位置で補い、count を超える余剰分も保持する
 * （marker_count を減らして戻したときに位置を復元するため）。
 */
const normalizeMarkers = (parsed, count) => {
    const length = Math.max(parsed.length, count);
    const markers = [];

    for (let i = 0; i < length; i++) {
        markers.push(normalizeMarker(parsed[i], i, count));
    }
    return markers;
};

/**
 * マーカーを markers ウィジェットへ書き戻す。
 * 余剰分を含む全件を直列化する（表示中の件数だけにすると位置の復元が成立しない）。
 */
const writeBackMarkers = (node, canvasWidget) => {
    const markersWidget = findWidgetByName(node, "markers");
    if (!markersWidget) return;

    const round = (value) => Number(value.toFixed(COORD_DIGITS));
    const serialized = canvasWidget.markers.map((marker) => ({ x: round(marker.x), y: round(marker.y) }));

    // markers 側の callback で自分の書き込みを読み返さないようにする
    canvasWidget.isWriting = true;
    markersWidget.value = JSON.stringify(serialized);
    canvasWidget.isWriting = false;
};

/**
 * marker_count に合わせて x_N / y_N の出力を増減する
 */
const syncOutputs = (node, count) => {
    // 不足分を追加。同名が既にあれば追加しない
    // （ワークフロー復元では serialize された出力が configure で先に復元されるため、
    //   無条件に addOutput すると重複する）
    for (let i = 1; i <= count; i++) {
        ["x", "y"].forEach((axis) => {
            const name = `${axis}_${i}`;
            if (!findOutputByName(node, name)) {
                node.addOutput(name, "*");
            }
        });
    }

    // 余剰分を削除。x_1 / y_1 は count >= 1 なので対象にならない
    const removeList = [];
    (node.outputs || []).forEach((output, index) => {
        const matched = output.name.match(/^[xy]_(\d+)$/);
        if (matched && parseInt(matched[1], 10) > count) {
            removeList.push(index);
        }
    });

    // インデックスがずれないように逆順で削除
    removeList.sort((a, b) => b - a).forEach((index) => node.removeOutput(index));

    node.setDirtyCanvas(true, true);
};

/**
 * キャンバスの高さを width / height のアスペクト比に追従させる
 */
const updateCanvasSize = (node) => {
    const size = node.computeSize();
    node.setSize([node.size[0], size[1]]);
    node.setDirtyCanvas(true, true);
};

/**
 * image ウィジェットの値から /view の URL を組み立てる。
 * modules/utils.js の getImageUrlFromApi は temp / output 用で type=input を付けられず、
 * input フォルダの画像が 404 になるためここで組み立てる。
 */
const buildImageUrl = (imageValue) => {
    let value = String(imageValue).trim();
    let type = "input";

    // "ファイル名 [input]" 形式の注釈を外す
    const annotated = value.match(/^(.*)\s+\[(\w+)\]$/);
    if (annotated) {
        value = annotated[1];
        type = annotated[2];
    }

    const separator = value.lastIndexOf("/");
    const subfolder = separator >= 0 ? value.substring(0, separator) : "";
    const filename = separator >= 0 ? value.substring(separator + 1) : value;

    const params = `filename=${encodeURIComponent(filename)}&type=${encodeURIComponent(type)}&subfolder=${encodeURIComponent(subfolder)}`;
    return api.apiURL(`/view?${params}`);
};

/**
 * 背景画像を読み込む。
 * updateSize はユーザーの選択・アップロード操作のときだけ true にする。
 * ワークフロー復元時に true にすると、手で変えて保存した width / height が潰れる。
 */
const loadCanvasImage = (node, updateSize) => {
    const canvasWidget = findWidgetByName(node, "canvas");
    const imageValue = findWidgetByName(node, "image")?.value ?? "";
    if (!canvasWidget) return;

    if (!imageValue) {
        canvasWidget.image = null;
        node.setDirtyCanvas(true, true);
        return;
    }

    const image = new Image();

    image.onload = () => {
        canvasWidget.image = image;

        if (updateSize) {
            const widthWidget = findWidgetByName(node, "width");
            const heightWidget = findWidgetByName(node, "height");
            if (widthWidget) widthWidget.value = image.naturalWidth;
            if (heightWidget) heightWidget.value = image.naturalHeight;
        }

        updateCanvasSize(node);
    };

    image.onerror = () => {
        canvasWidget.image = null;
        node.setDirtyCanvas(true, true);
    };

    image.src = buildImageUrl(imageValue);
};

/**
 * markers ウィジェットの値・出力・背景画像をノードへ反映する
 */
const refreshFromWidgets = (node, updateSize) => {
    const canvasWidget = findWidgetByName(node, "canvas");
    const markersWidget = findWidgetByName(node, "markers");
    if (!canvasWidget) return;

    const count = getNumber(node, "marker_count", 1);
    const parsed = tryParseMarkers(markersWidget?.value ?? "[]") ?? [];

    canvasWidget.markers = normalizeMarkers(parsed, count);
    syncOutputs(node, count);
    loadCanvasImage(node, updateSize);
    updateCanvasSize(node);
};

/**
 * 背景を描く。画像があれば座標系いっぱいに引き伸ばす
 */
const drawBackground = (ctx, rect, image) => {
    ctx.fillStyle = "#1a1a1a";
    ctx.fillRect(rect.x, rect.y, rect.w, rect.h);

    if (image) {
        ctx.drawImage(image, rect.x, rect.y, rect.w, rect.h);
    } else {
        // 位置の目安になるガイド線
        ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        [0.25, 0.5, 0.75].forEach((ratio) => {
            const x = Math.round(rect.x + rect.w * ratio) + 0.5;
            const y = Math.round(rect.y + rect.h * ratio) + 0.5;
            ctx.moveTo(x, rect.y);
            ctx.lineTo(x, rect.y + rect.h);
            ctx.moveTo(rect.x, y);
            ctx.lineTo(rect.x + rect.w, y);
        });
        ctx.stroke();
    }

    ctx.strokeStyle = "#555555";
    ctx.lineWidth = 1;
    ctx.strokeRect(rect.x + 0.5, rect.y + 0.5, rect.w - 1, rect.h - 1);
};

/**
 * マーカーの表示色。連番から離れた色相を作る
 */
const markerColor = (index) => `hsl(${(index * 137.5) % 360}, 70%, 55%)`;

/**
 * ドラッグ中のマーカーに表示する現在値
 */
const formatMarkerLabel = (node, marker) => {
    const mode = findWidgetByName(node, "mode")?.value;

    if (mode === MODE_ABSOLUTE) {
        const width = getNumber(node, "width", 1024);
        const height = getNumber(node, "height", 1024);
        return `${Math.round(marker.x * width)}, ${Math.round(marker.y * height)}`;
    }
    return `${marker.x.toFixed(3)}, ${marker.y.toFixed(3)}`;
};

/**
 * マーカーを描く。marker_count を超える余剰分は描かない
 */
const drawMarkers = (ctx, node, rect, markers, count, dragIndex) => {
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    for (let i = 0; i < count && i < markers.length; i++) {
        const cx = rect.x + markers[i].x * rect.w;
        const cy = rect.y + markers[i].y * rect.h;

        ctx.beginPath();
        ctx.arc(cx, cy, MARKER_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = markerColor(i);
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = "#000000";
        ctx.font = "bold 11px Arial";
        ctx.fillText(String(i + 1), cx, cy + 0.5);

        if (i === dragIndex) {
            const label = formatMarkerLabel(node, markers[i]);
            ctx.font = "11px Arial";
            const textWidth = ctx.measureText(label).width;
            const boxY = cy - MARKER_RADIUS - 18;

            ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
            ctx.fillRect(cx - textWidth / 2 - 4, boxY, textWidth + 8, 16);
            ctx.fillStyle = "#ffffff";
            ctx.fillText(label, cx, boxY + 8);
        }
    }
};

/**
 * 掴んだマーカーの番号を返す。掴めなければ -1。
 * 同距離なら番号が大きいほう（後から描かれて手前に見えているほう）を優先する。
 */
const findNearestMarker = (markers, count, rect, localX, localY) => {
    let found = -1;
    let nearest = GRAB_RADIUS;

    for (let i = 0; i < count && i < markers.length; i++) {
        const dx = markers[i].x * rect.w - localX;
        const dy = markers[i].y * rect.h - localY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance <= nearest) {
            nearest = distance;
            found = i;
        }
    }
    return found;
};

/**
 * マーカーのドラッグを開始する。
 *
 * 終了検知が素直にいかない理由:
 * - `widget.mouse` には pointerdown と pointerup しか届かず、move が来ない。
 * - document の pointerup も **bubble 段階では届かない**。
 *   `LGraphCanvas.processMouseUp` がクリック時（ドラッグ無し）に
 *   `e.stopPropagation()` するため、リスナーが外れず「クリックしただけで
 *   マーカーがマウスに追従し続ける」状態になる。
 *
 * そこで move は document の **capture 段階**で受け、終了は
 * (1) `widget.mouse` の pointerup、(2) document capture の pointerup、
 * (3) ボタンを離した状態の pointermove の3経路から idempotent に閉じる。
 */
const startDrag = (node, canvasWidget, index, event) => {
    const rect = canvasWidget.rect;
    const scale = app.canvas?.ds?.scale ?? 1;
    const startX = event.clientX;
    const startY = event.clientY;
    const origin = { ...canvasWidget.markers[index] };

    const onMove = (moveEvent) => {
        // ボタンが離れている = どこかで pointerup を取りこぼしている
        if (!moveEvent.buttons) {
            canvasWidget.endDrag();
            return;
        }

        const dx = (moveEvent.clientX - startX) / scale / rect.w;
        const dy = (moveEvent.clientY - startY) / scale / rect.h;

        canvasWidget.markers[index] = {
            x: Math.min(1, Math.max(0, origin.x + dx)),
            y: Math.min(1, Math.max(0, origin.y + dy)),
        };
        node.setDirtyCanvas(true, true);
    };

    const onUp = () => canvasWidget.endDrag();

    canvasWidget.dragIndex = index;

    canvasWidget.endDrag = () => {
        // 3経路から呼ばれるので多重呼び出しを弾く
        if (canvasWidget.dragIndex < 0) return;
        canvasWidget.dragIndex = -1;

        document.removeEventListener("pointermove", onMove, true);
        document.removeEventListener("pointerup", onUp, true);

        // 書き戻しはドラッグ終了時だけ
        writeBackMarkers(node, canvasWidget);
        node.setDirtyCanvas(true, true);
    };

    document.addEventListener("pointermove", onMove, true);
    document.addEventListener("pointerup", onUp, true);
};


///////////////////////////
///////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_CreatePoint",

    /**
     * D2_MARKER_CANVAS マーカーを表示・ドラッグするキャンバス
     */
    getCustomWidgets(app) {
        return {
            D2_MARKER_CANVAS(node, inputName, inputData, app) {
                // value は不活性な固定値。マーカーの実データは markers ウィジェットが持つ
                const widget = getReadOnlyWidgetBase(node, "D2_MARKER_CANVAS", inputName, "");

                widget.markers = [];
                widget.image = null;
                widget.rect = null;
                // 高さ上限で幅を縮めたときの実キャンバス幅。computeSize が設定する
                widget.canvasWidth = null;
                widget.dragIndex = -1;
                widget.isWriting = false;
                // ドラッグ中だけ startDrag が差し替える
                widget.endDrag = () => {};

                widget.computeSize = function (width) {
                    // ノードのウィジェット配置（_arrangeWidgets）は computeSize() を引数なしで呼び、
                    // ノードサイズ計算（LGraphNode.computeSize）は幅付きで呼ぶ。
                    // 引数なしのまま width で計算すると NaN になり、computedHeight → 後続ウィジェットの y
                    // まで NaN が伝播して DOM ウィジェット（markers）が画面外へ飛ぶ。
                    const nodeWidth = Number.isFinite(width) ? width : (node.size?.[0] ?? DEFAULT_NODE_WIDTH);
                    const available = Math.max(nodeWidth - CANVAS_MARGIN * 2, 1);
                    const ratio = getNumber(node, "height", 1024) / getNumber(node, "width", 1024);

                    let canvasWidth = available;
                    let height = Math.round(available * ratio);

                    // 上限に当たったら、高さを切るだけでなく幅も縮めてアスペクト比を保つ。
                    // 高さだけ切ると画像とマーカー配置が横に引き伸ばされ、
                    // 「実際の位置を見て決める」というこのノードの目的が崩れる。
                    if (Number.isFinite(ratio) && ratio > 0 && height > CANVAS_MAX_HEIGHT) {
                        height = CANVAS_MAX_HEIGHT;
                        canvasWidth = Math.max(Math.round(height / ratio), 1);
                    }

                    // 幅・高さが不正でも必ず有限値を返す
                    const safeHeight = Number.isFinite(height) && height > 0 ? height : MIN_CANVAS_HEIGHT;

                    this.canvasWidth = Math.min(canvasWidth, available);
                    this.size = [nodeWidth, safeHeight];
                    return [nodeWidth, safeHeight];
                };

                widget.draw = function (ctx, node, width, y) {
                    // 高さ上限で幅を縮めた場合は中央寄せにする
                    const available = Math.max(width - CANVAS_MARGIN * 2, 1);
                    const canvasWidth = Math.min(this.canvasWidth ?? available, available);

                    const rect = {
                        x: Math.round((width - canvasWidth) / 2),
                        y: y,
                        w: canvasWidth,
                        h: this.size[1],
                    };
                    this.rect = rect;

                    const count = getNumber(node, "marker_count", 1);
                    drawBackground(ctx, rect, this.image);
                    drawMarkers(ctx, node, rect, this.markers, count, this.dragIndex);
                };

                widget.mouse = function (event, pos, node) {
                    // ドラッグ終了の主経路。processWidgetClick が仕込む pointer.finally 経由で
                    // pointerup が届き、processMouseUp の stopPropagation より前に呼ばれる。
                    if (event.type === "pointerup") {
                        this.endDrag();
                        return false;
                    }

                    if (event.type !== "pointerdown" || !this.rect) return false;

                    const localX = pos[0] - this.rect.x;
                    const localY = pos[1] - this.rect.y;
                    if (localX < 0 || localY < 0 || localX > this.rect.w || localY > this.rect.h) return false;

                    const count = getNumber(node, "marker_count", 1);
                    const index = findNearestMarker(this.markers, count, this.rect, localX, localY);
                    if (index < 0) return false;

                    startDrag(node, this, index, event);
                    return true;
                };

                node.addCustomWidget(widget);
            },
        };
    },

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_TITLE) return;

        /**
         * ノード作成
         * ウィジェットの連動を設定する
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const node = this;
            const canvasWidget = findWidgetByName(node, "canvas");
            const countWidget = findWidgetByName(node, "marker_count");
            const markersWidget = findWidgetByName(node, "markers");
            const imageWidget = findWidgetByName(node, "image");

            // marker_count の変更を検知して出力とマーカーを増減する
            if (countWidget) {
                let countValue = countWidget.value;

                Object.defineProperty(countWidget, "value", {
                    get() {
                        return countValue;
                    },
                    set(newValue) {
                        if (newValue === countValue) return;
                        countValue = newValue;

                        syncOutputs(node, newValue);

                        if (canvasWidget) {
                            canvasWidget.markers = normalizeMarkers(canvasWidget.markers, newValue);
                            writeBackMarkers(node, canvasWidget);
                        }
                        node.setDirtyCanvas(true, true);
                    },
                });
            }

            // markers を手編集したらキャンバスへ反映する
            if (markersWidget && canvasWidget) {
                markersWidget.callback = () => {
                    if (canvasWidget.isWriting) return;

                    // パースできないときは何もしない
                    // （入力途中の壊れた JSON でマーカーが消えるのを防ぐ）
                    const parsed = tryParseMarkers(markersWidget.value);
                    if (!parsed) return;

                    canvasWidget.markers = normalizeMarkers(parsed, getNumber(node, "marker_count", 1));
                    node.setDirtyCanvas(true, true);
                };
            }

            // width / height を変えたらキャンバスのアスペクト比を追従させる
            ["width", "height"].forEach((name) => {
                const widget = findWidgetByName(node, name);
                if (!widget) return;

                const origCallback = widget.callback;
                widget.callback = function (...args) {
                    const result = origCallback ? origCallback.apply(this, args) : undefined;
                    updateCanvasSize(node);
                    return result;
                };
            });

            // 標準の callback は setNodeOutputs でノード背景に画像プレビューを出す（node.imgs）。
            // 自前キャンバスと二重に表示されるので差し替える。
            if (imageWidget) {
                imageWidget.callback = () => {
                    node.imgs = undefined;
                    loadCanvasImage(node, true);
                };
            }

            // このノードは自前キャンバスに画像を描くので、組み込みのサムネイル表示は殺す。
            // プレビュー描画は addDrawBackgroundHandler が仕込む onDrawBackground →
            // updatePreviews に一本化されているため、ここを潰せば経路ごと塞げる
            // （setNodeOutputs を誰が呼んだかに関係なく効く）。
            // prototype ではなくインスタンスに生やして、このノードだけに閉じる。
            node.onDrawBackground = () => {};

            refreshFromWidgets(node, false);

            return r;
        };

        /**
         * ワークフロー復元
         * 背景画像だけ読み直す。width / height には触らない
         */
        const origOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (info) {
            const result = origOnConfigure ? origOnConfigure.apply(this, arguments) : undefined;
            refreshFromWidgets(this, false);
            return result;
        };
    },
});
