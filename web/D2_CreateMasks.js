import { app } from "/scripts/app.js";
import { findWidgetByName, findOutputByName, getReadOnlyWidgetBase } from "./modules/utils.js";
import { CANVAS_MARGIN, computeCanvasSize, buildInputImageUrl } from "./modules/util_node_canvas.js";

const NODE_TITLE = "D2 Create Masks";

// 丸数字とリサイズハンドルの半径
const MARKER_RADIUS = 10;

// リサイズハンドルを掴める距離
const HANDLE_GRAB_RADIUS = 12;

// 座標 JSON の小数桁。6桁なら最大解像度 16384px でも 0.02px 未満の誤差に収まる
const COORD_DIGITS = 6;

// nodes/modules/mask_rect_util.py と同じ値にすること
const DEFAULT_MASK_SIZE = 0.25;
const DEFAULT_MASK_ORIGIN = 0.375;
const MASK_OFFSET_STEP = 0.02;
const MIN_MASK_SIZE = 0.01;

// 四隅の識別子。[x が左か, y が上か] で持つと対角の算出が素直に書ける
const CORNERS = [
    { left: true, top: true },
    { left: false, top: true },
    { left: true, top: false },
    { left: false, top: false },
];


/**
 * マスクの既定矩形（相対値）。中央 1/4 サイズを番号ごとに右下へずらす。
 * nodes/modules/mask_rect_util.py の default_mask_rect と同じ式にすること。
 * ここがズレると、実行するまで気づかないマスク位置の食い違いになる。
 */
const defaultMaskRect = (index) => {
    const offset = index * MASK_OFFSET_STEP;
    return {
        x: DEFAULT_MASK_ORIGIN + offset,
        y: DEFAULT_MASK_ORIGIN + offset,
        w: DEFAULT_MASK_SIZE,
        h: DEFAULT_MASK_SIZE,
    };
};

/**
 * min〜max に収める。数値として扱えなければ null
 */
const clamp = (value, min, max) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return null;
    return Math.min(max, Math.max(min, num));
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
 * 矩形1件を正規化する。取り出せなければ既定矩形。
 * はみ出しは位置を内側へ押し戻して吸収し、幅・高さは縮めない。
 * nodes/modules/mask_rect_util.py の normalize_rect と揃えること。
 */
const normalizeRect = (rect, index) => {
    if (rect === null || typeof rect !== "object") return defaultMaskRect(index);

    const x = clamp(rect.x, 0, 1);
    const y = clamp(rect.y, 0, 1);
    const w = clamp(rect.w, MIN_MASK_SIZE, 1);
    const h = clamp(rect.h, MIN_MASK_SIZE, 1);
    if (x === null || y === null || w === null || h === null) return defaultMaskRect(index);

    return { x: Math.min(x, 1 - w), y: Math.min(y, 1 - h), w, h };
};

/**
 * JSON をパースして配列を返す。壊れていれば null
 */
const tryParseMasks = (masksJson) => {
    try {
        const parsed = JSON.parse(masksJson);
        return Array.isArray(parsed) ? parsed : null;
    } catch (e) {
        return null;
    }
};

/**
 * パース済み配列を正規化する。
 * count に満たない分は既定矩形で補い、count を超える余剰分も保持する
 * （mask_count を減らして戻したときに矩形を復元するため）。
 */
const normalizeMasks = (parsed, count) => {
    const length = Math.max(parsed.length, count);
    const masks = [];

    for (let i = 0; i < length; i++) {
        masks.push(normalizeRect(parsed[i], i));
    }
    return masks;
};

/**
 * マスクを masks ウィジェットへ書き戻す。
 * 余剰分を含む全件を直列化する（表示中の件数だけにすると矩形の復元が成立しない）。
 */
const writeBackMasks = (node, canvasWidget) => {
    const masksWidget = findWidgetByName(node, "masks");
    if (!masksWidget) return;

    const round = (value) => Number(value.toFixed(COORD_DIGITS));
    const serialized = canvasWidget.masks.map((rect) => ({
        x: round(rect.x),
        y: round(rect.y),
        w: round(rect.w),
        h: round(rect.h),
    }));

    // masks 側の callback で自分の書き込みを読み返さないようにする
    canvasWidget.isWriting = true;
    masksWidget.value = JSON.stringify(serialized);
    canvasWidget.isWriting = false;
};

/**
 * mask_count に合わせて mask_N の出力を増減する
 */
const syncOutputs = (node, count) => {
    // 不足分を追加。同名が既にあれば追加しない
    // （ワークフロー復元では serialize された出力が configure で先に復元されるため、
    //   無条件に addOutput すると重複する）
    for (let i = 1; i <= count; i++) {
        const name = `mask_${i}`;
        if (!findOutputByName(node, name)) {
            node.addOutput(name, "MASK");
        }
    }

    // 余剰分を削除。mask_1 は count >= 1 なので対象にならない
    const removeList = [];
    (node.outputs || []).forEach((output, index) => {
        const matched = output.name.match(/^mask_(\d+)$/);
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
 * アクティブなマスクの番号（0 始まり）。mask_count の範囲に収める
 */
const getActiveIndex = (node, canvasWidget) => {
    const count = getNumber(node, "mask_count", 1);
    return Math.min(Math.max(canvasWidget.activeIndex, 0), count - 1);
};

/**
 * アクティブなマスクを変える。select_mask ウィジェットへも反映する。
 * isSyncing は select_mask 側の setter から戻ってこないようにするためのもの。
 */
const setActiveMask = (node, canvasWidget, index) => {
    canvasWidget.activeIndex = index;

    const selectWidget = findWidgetByName(node, "select_mask");
    if (!selectWidget || selectWidget.value === index + 1) return;

    canvasWidget.isSyncing = true;
    selectWidget.value = index + 1;
    canvasWidget.isSyncing = false;

    node.setDirtyCanvas(true, true);
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
 * マスクの表示色。連番から離れた色相を作る（D2 Create Point のマーカーと同じ式）
 */
const maskHue = (index) => (index * 137.5) % 360;

/**
 * 相対矩形をキャンバス上のピクセル矩形に直す
 */
const rectToCanvas = (rect, maskRect) => ({
    x: rect.x + maskRect.x * rect.w,
    y: rect.y + maskRect.y * rect.h,
    w: maskRect.w * rect.w,
    h: maskRect.h * rect.h,
});

/**
 * 矩形の四隅の座標を CORNERS と同じ順で返す
 */
const cornerPositions = (box) => CORNERS.map((corner) => ({
    x: corner.left ? box.x : box.x + box.w,
    y: corner.top ? box.y : box.y + box.h,
}));

/**
 * 丸数字を描く。D2 Create Point のマーカーと同じ見た目
 */
const drawNumber = (ctx, cx, cy, index) => {
    ctx.beginPath();
    ctx.arc(cx, cy, MARKER_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${maskHue(index)}, 70%, 55%)`;
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = "#000000";
    ctx.font = "bold 11px Arial";
    ctx.fillText(String(index + 1), cx, cy + 0.5);
};

/**
 * リサイズハンドル（丸数字と同じサイズの白丸）を四隅に描く
 */
const drawHandles = (ctx, box, index) => {
    ctx.fillStyle = "#ffffff";
    ctx.strokeStyle = `hsl(${maskHue(index)}, 70%, 55%)`;
    ctx.lineWidth = 2;

    cornerPositions(box).forEach((corner) => {
        ctx.beginPath();
        ctx.arc(corner.x, corner.y, MARKER_RADIUS, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
    });
};

/**
 * ドラッグ中のマスクに表示する現在値（ピクセル換算）
 */
const formatRectLabel = (node, maskRect) => {
    const width = getNumber(node, "width", 1024);
    const height = getNumber(node, "height", 1024);
    const x = Math.round(maskRect.x * width);
    const y = Math.round(maskRect.y * height);
    const w = Math.round(maskRect.w * width);
    const h = Math.round(maskRect.h * height);
    return `${x}, ${y}  ${w} × ${h}`;
};

/**
 * ドラッグ中の値ラベルを矩形の左上に描く
 */
const drawLabel = (ctx, box, label) => {
    ctx.font = "11px Arial";
    ctx.textAlign = "left";

    const textWidth = ctx.measureText(label).width;
    const boxY = box.y - 18;

    ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
    ctx.fillRect(box.x, boxY, textWidth + 8, 16);
    ctx.fillStyle = "#ffffff";
    ctx.fillText(label, box.x + 4, boxY + 8);

    ctx.textAlign = "center";
};

/**
 * マスク1件を描く。アクティブなら枠線を太くして四隅にハンドルを出す
 */
const drawMask = (ctx, node, rect, maskRect, index, isActive, showLabel) => {
    const box = rectToCanvas(rect, maskRect);

    ctx.fillStyle = `hsla(${maskHue(index)}, 70%, 55%, 0.3)`;
    ctx.fillRect(box.x, box.y, box.w, box.h);

    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = isActive ? 2 : 1;
    ctx.strokeRect(box.x, box.y, box.w, box.h);

    drawNumber(ctx, box.x + box.w / 2, box.y + box.h / 2, index);

    if (isActive) drawHandles(ctx, box, index);
    if (showLabel) drawLabel(ctx, box, formatRectLabel(node, maskRect));
};

/**
 * 掴んだリサイズハンドルの番号を返す。掴めなければ -1。
 * 座標は rectToCanvas と同じキャンバス絶対座標で渡すこと
 */
const findCorner = (box, pointX, pointY) => {
    const corners = cornerPositions(box);

    for (let i = 0; i < corners.length; i++) {
        const dx = corners[i].x - pointX;
        const dy = corners[i].y - pointY;
        if (Math.sqrt(dx * dx + dy * dy) <= HANDLE_GRAB_RADIUS) return i;
    }
    return -1;
};

/**
 * 指定位置にあるマスクの番号を返す。無ければ -1。
 * 手前に見えているもの（アクティブ → 番号の大きい順）を優先する。
 * 座標は rectToCanvas と同じキャンバス絶対座標で渡すこと
 */
const findMaskAt = (masks, count, rect, pointX, pointY, activeIndex) => {
    const isInside = (index) => {
        const box = rectToCanvas(rect, masks[index]);
        return pointX >= box.x && pointX <= box.x + box.w && pointY >= box.y && pointY <= box.y + box.h;
    };

    if (activeIndex >= 0 && activeIndex < count && activeIndex < masks.length && isInside(activeIndex)) {
        return activeIndex;
    }

    for (let i = Math.min(count, masks.length) - 1; i >= 0; i--) {
        if (isInside(i)) return i;
    }
    return -1;
};

/**
 * 1軸ぶんのリサイズ。fixed（対角の座標）を固定して moving 側を動かす。
 * 対角を越えたら Math.min / Math.abs がそのまま反転を吸収する。
 */
const resizeAxis = (fixed, moving) => {
    const clamped = Math.min(1, Math.max(0, moving));
    let start = Math.min(fixed, clamped);
    let size = Math.abs(clamped - fixed);

    if (size < MIN_MASK_SIZE) {
        size = MIN_MASK_SIZE;
        // 潰れたときは掴んでいる側へ最小サイズを確保する
        start = clamped >= fixed ? fixed : fixed - size;
        start = Math.min(Math.max(start, 0), 1 - size);
    }
    return { start, size };
};

/**
 * ドラッグの土台。移動量を相対値で onMove に渡し、終了処理をまとめる。
 *
 * 終了検知が素直にいかない理由（.claude/knowledge.md 2026-08-26）:
 * - `widget.mouse` には pointerdown と pointerup しか届かず、move が来ない。
 * - document の pointerup も **bubble 段階では届かない**。
 *   `LGraphCanvas.processMouseUp` がクリック時（ドラッグ無し）に `e.stopPropagation()` するため。
 *
 * そこで move は document の **capture 段階**で受け、終了は
 * (1) `widget.mouse` の pointerup、(2) document capture の pointerup、
 * (3) ボタンを離した状態の pointermove の3経路から idempotent に閉じる。
 */
const startDrag = (node, canvasWidget, event, onMove) => {
    const rect = canvasWidget.rect;
    const scale = app.canvas?.ds?.scale ?? 1;
    const startX = event.clientX;
    const startY = event.clientY;

    const handleMove = (moveEvent) => {
        // ボタンが離れている = どこかで pointerup を取りこぼしている
        if (!moveEvent.buttons) {
            canvasWidget.endDrag();
            return;
        }

        onMove(
            (moveEvent.clientX - startX) / scale / rect.w,
            (moveEvent.clientY - startY) / scale / rect.h,
        );
        node.setDirtyCanvas(true, true);
    };

    const handleUp = () => canvasWidget.endDrag();

    canvasWidget.isDragging = true;

    canvasWidget.endDrag = () => {
        // 3経路から呼ばれるので多重呼び出しを弾く
        if (!canvasWidget.isDragging) return;
        canvasWidget.isDragging = false;

        document.removeEventListener("pointermove", handleMove, true);
        document.removeEventListener("pointerup", handleUp, true);

        // 書き戻しはドラッグ終了時だけ
        writeBackMasks(node, canvasWidget);
        node.setDirtyCanvas(true, true);
    };

    document.addEventListener("pointermove", handleMove, true);
    document.addEventListener("pointerup", handleUp, true);
};

/**
 * マスクの移動を開始する。端では止まり、サイズは変えない
 */
const startMove = (node, canvasWidget, index, event) => {
    const origin = { ...canvasWidget.masks[index] };

    startDrag(node, canvasWidget, event, (dx, dy) => {
        canvasWidget.masks[index] = {
            x: Math.min(Math.max(origin.x + dx, 0), 1 - origin.w),
            y: Math.min(Math.max(origin.y + dy, 0), 1 - origin.h),
            w: origin.w,
            h: origin.h,
        };
    });
};

/**
 * マスクのリサイズを開始する。掴んだ角の対角を固定して反対の角を動かす。
 * ドラッグ中は掴み替えをせず、最初に掴んだ角を動かし続ける
 */
const startResize = (node, canvasWidget, index, cornerIndex, event) => {
    const origin = { ...canvasWidget.masks[index] };
    const corner = CORNERS[cornerIndex];

    // 固定する対角の座標と、掴んでいる角の開始座標
    const fixedX = corner.left ? origin.x + origin.w : origin.x;
    const fixedY = corner.top ? origin.y + origin.h : origin.y;
    const movingX = corner.left ? origin.x : origin.x + origin.w;
    const movingY = corner.top ? origin.y : origin.y + origin.h;

    startDrag(node, canvasWidget, event, (dx, dy) => {
        const horizontal = resizeAxis(fixedX, movingX + dx);
        const vertical = resizeAxis(fixedY, movingY + dy);

        canvasWidget.masks[index] = {
            x: horizontal.start,
            y: vertical.start,
            w: horizontal.size,
            h: vertical.size,
        };
    });
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

    image.src = buildInputImageUrl(imageValue);
};

/**
 * masks ウィジェットの値・出力・背景画像をノードへ反映する
 */
const refreshFromWidgets = (node, updateSize) => {
    const canvasWidget = findWidgetByName(node, "canvas");
    const masksWidget = findWidgetByName(node, "masks");
    if (!canvasWidget) return;

    const count = getNumber(node, "mask_count", 1);
    const parsed = tryParseMasks(masksWidget?.value ?? "[]") ?? [];

    canvasWidget.masks = normalizeMasks(parsed, count);
    canvasWidget.activeIndex = getNumber(node, "select_mask", 1) - 1;
    syncOutputs(node, count);
    loadCanvasImage(node, updateSize);
    updateCanvasSize(node);
};


///////////////////////////
///////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_CreateMasks",

    /**
     * D2_MASK_CANVAS 長方形マスクを表示・ドラッグするキャンバス
     */
    getCustomWidgets(app) {
        return {
            D2_MASK_CANVAS(node, inputName, inputData, app) {
                // value は不活性な固定値。マスクの実データは masks ウィジェットが持つ
                const widget = getReadOnlyWidgetBase(node, "D2_MASK_CANVAS", inputName, "");

                widget.masks = [];
                widget.image = null;
                widget.rect = null;
                // 高さ上限で幅を縮めたときの実キャンバス幅。computeSize が設定する
                widget.canvasWidth = null;
                widget.activeIndex = 0;
                widget.isDragging = false;
                widget.isWriting = false;
                widget.isSyncing = false;
                // ドラッグ中だけ startDrag が差し替える
                widget.endDrag = () => {};

                widget.computeSize = function (width) {
                    const ratio = getNumber(node, "height", 1024) / getNumber(node, "width", 1024);
                    const size = computeCanvasSize(width, ratio, node.size?.[0]);

                    this.canvasWidth = size.canvasWidth;
                    this.size = [size.nodeWidth, size.height];
                    return [size.nodeWidth, size.height];
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

                    const count = getNumber(node, "mask_count", 1);
                    const active = getActiveIndex(node, this);

                    drawBackground(ctx, rect, this.image);

                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";

                    // 番号順に描き、アクティブなものだけ最後に描いて最前面にする
                    for (let i = 0; i < count && i < this.masks.length; i++) {
                        if (i !== active) drawMask(ctx, node, rect, this.masks[i], i, false, false);
                    }
                    if (active < this.masks.length) {
                        drawMask(ctx, node, rect, this.masks[active], active, true, this.isDragging);
                    }
                };

                widget.mouse = function (event, pos, node) {
                    // ドラッグ終了の主経路。processWidgetClick が仕込む pointer.finally 経由で
                    // pointerup が届き、processMouseUp の stopPropagation より前に呼ばれる。
                    if (event.type === "pointerup") {
                        this.endDrag();
                        return false;
                    }

                    if (event.type !== "pointerdown" || !this.rect) return false;

                    // pos と rect は同じ座標系（ノード内のウィジェット座標）なので、
                    // 範囲チェックだけキャンバス左上を原点に直して行う
                    const localX = pos[0] - this.rect.x;
                    const localY = pos[1] - this.rect.y;
                    if (localX < 0 || localY < 0 || localX > this.rect.w || localY > this.rect.h) return false;

                    const count = getNumber(node, "mask_count", 1);
                    const active = getActiveIndex(node, this);

                    // アクティブなマスクの四隅ハンドルが最優先
                    if (active < this.masks.length) {
                        const box = rectToCanvas(this.rect, this.masks[active]);
                        const corner = findCorner(box, pos[0], pos[1]);
                        if (corner >= 0) {
                            startResize(node, this, active, corner, event);
                            return true;
                        }
                    }

                    const index = findMaskAt(this.masks, count, this.rect, pos[0], pos[1], active);
                    if (index < 0) return false;

                    setActiveMask(node, this, index);
                    startMove(node, this, index, event);
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
            const countWidget = findWidgetByName(node, "mask_count");
            const selectWidget = findWidgetByName(node, "select_mask");
            const masksWidget = findWidgetByName(node, "masks");
            const imageWidget = findWidgetByName(node, "image");

            // mask_count の変更を検知して出力とマスクを増減する
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
                            canvasWidget.masks = normalizeMasks(canvasWidget.masks, newValue);
                            writeBackMasks(node, canvasWidget);
                        }

                        // 表示されなくなった番号を指したままにしない
                        if (selectWidget && selectWidget.value > newValue) {
                            selectWidget.value = newValue;
                        }
                        node.setDirtyCanvas(true, true);
                    },
                });
            }

            // select_mask の変更でアクティブなマスクを切り替える
            if (selectWidget && canvasWidget) {
                let selectValue = selectWidget.value;

                Object.defineProperty(selectWidget, "value", {
                    get() {
                        return selectValue;
                    },
                    set(newValue) {
                        const count = getNumber(node, "mask_count", 1);
                        const clamped = Math.min(Math.max(Number(newValue) || 1, 1), count);
                        if (clamped === selectValue) return;
                        selectValue = clamped;

                        // キャンバス発の更新なら activeIndex は設定済みなので触らない
                        if (!canvasWidget.isSyncing) {
                            canvasWidget.activeIndex = clamped - 1;
                            node.setDirtyCanvas(true, true);
                        }
                    },
                });
            }

            // masks を手編集したらキャンバスへ反映する
            if (masksWidget && canvasWidget) {
                masksWidget.callback = () => {
                    if (canvasWidget.isWriting) return;

                    // パースできないときは何もしない
                    // （入力途中の壊れた JSON でマスクが消えるのを防ぐ）
                    const parsed = tryParseMasks(masksWidget.value);
                    if (!parsed) return;

                    canvasWidget.masks = normalizeMasks(parsed, getNumber(node, "mask_count", 1));
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
            // updatePreviews に一本化されているため、ここを潰せば経路ごと塞げる。
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
