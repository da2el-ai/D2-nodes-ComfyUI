import { api } from "../../../scripts/api.js";

/**
 * ノード内キャンバスを持つノード（D2 Create Point / D2 Create Masks）の共有ユーティリティ。
 * 描画・ヒット判定・ドラッグはノードごとに操作モデルが違うので共有しない。
 * ここに置くのは、どちらでも同じ結果になるべき純粋な計算だけ。
 */

// キャンバスの左右余白
const CANVAS_MARGIN = 10;

// キャンバスの高さ上限。これを超えるとノードが縦に伸びすぎて扱いにくい
const CANVAS_MAX_HEIGHT = 1280;

// 高さが算出できなかったときの最低限の高さ
const MIN_CANVAS_HEIGHT = 64;

// computeSize が引数なしで呼ばれ、かつノード幅もまだ無いときの保険
const DEFAULT_NODE_WIDTH = 240;


/**
 * キャンバスの表示サイズを算出する。
 *
 * ノードのウィジェット配置（_arrangeWidgets）は computeSize() を引数なしで呼び、
 * ノードサイズ計算（LGraphNode.computeSize）だけが幅付きで呼ぶ。引数なしのまま
 * 計算すると NaN になり、computedHeight → 後続ウィジェットの y まで NaN が伝播して
 * DOM ウィジェットが画面外へ飛ぶ。そのため戻り値は必ず有限値にする。
 *
 * 高さ上限に当たったときは高さを切るだけでなく幅も縮めてアスペクト比を保つ。
 * 高さだけ切ると内容が横に引き伸ばされ、「実際の位置を見て決める」という
 * これらのノードの目的が崩れるため。canvasWidth < nodeWidth なら中央寄せにする。
 *
 * @param {number} width - computeSize に渡された幅（undefined の場合あり）
 * @param {number} ratio - 縦横比（height / width）
 * @param {number} fallbackWidth - width が無いときに使うノード幅
 * @returns {{nodeWidth: number, canvasWidth: number, height: number}}
 */
const computeCanvasSize = (width, ratio, fallbackWidth) => {
    const nodeWidth = Number.isFinite(width)
        ? width
        : (Number.isFinite(fallbackWidth) ? fallbackWidth : DEFAULT_NODE_WIDTH);
    const available = Math.max(nodeWidth - CANVAS_MARGIN * 2, 1);

    let canvasWidth = available;
    let height = Math.round(available * ratio);

    if (Number.isFinite(ratio) && ratio > 0 && height > CANVAS_MAX_HEIGHT) {
        height = CANVAS_MAX_HEIGHT;
        canvasWidth = Math.max(Math.round(height / ratio), 1);
    }

    return {
        nodeWidth,
        canvasWidth: Math.min(canvasWidth, available),
        height: Number.isFinite(height) && height > 0 ? height : MIN_CANVAS_HEIGHT,
    };
};


/**
 * image ウィジェットの値から /view の URL を組み立てる。
 * modules/utils.js の getImageUrlFromApi は temp / output 用で type=input を付けられず、
 * input フォルダの画像が 404 になるためここで組み立てる。
 */
const buildInputImageUrl = (imageValue) => {
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


export {
    CANVAS_MARGIN,
    computeCanvasSize,
    buildInputImageUrl,
};
