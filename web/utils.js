
/**
 * 指定ミリ秒待機
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * ウィジェットを名前から探す
 */
const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

/**
 * ウィジェットを名前から探す
 * "converted-widget" なら inputs から探す
 */
const findWidgetOrInputsByName = (node, name) => {
    const widget = findWidgetByName(node, name);
    if (widget.type !== "converted-widget") return widget;
    return node.inputs ? node.inputs.find((w) => w.name === name) : null;
};


/**
 * ウィジェットをタイプから探す
 */
const findWidgetByType = (node, type) => {
    return node.widgets ? node.widgets.find((w) => w.type === type) : null;
};

/**
 * クッキーに保存
 * @param {string} cookieName 
 * @param {any} obj 
 */
const setCookie = (cookieName, obj) => {
    const jsonString = JSON.stringify(obj);
    const encodedJsonString = encodeURIComponent(jsonString);
    const farFuture = new Date();
    farFuture.setFullYear(farFuture.getFullYear() + 100);
    document.cookie = `${cookieName}=${encodedJsonString}; expires=${farFuture.toUTCString()}; path=/`;
}

/**
 * クッキーから取得
 * @param {string} cookieName 
 * @returns any
 */
const getCookie = (cookieName) => {
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(cookieName + "=")) {
            const encodedJsonString = cookie.substring(cookieName.length + 1);
            const jsonString = decodeURIComponent(encodedJsonString);
            return JSON.parse(jsonString);
        }
    }
    return undefined;
}

/**
 * CSSを動的に読み込む
 */
const loadCssFile = (filePath) => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = filePath;
    document.head.appendChild(link);
}

/**
 * widget inputs に存在するか
 */
const doesInputWithNameExist = (node, name) => {
    return node.inputs ? node.inputs.some((input) => input.name === name) : false;
};

/**
 * widget の表示・非表示切り替え
 */
let origProps = {};
const HIDDEN_TAG = "d2hide";

function toggleWidget(node, widget, show = false, suffix = "") {
    if (!widget || doesInputWithNameExist(node, widget.name)) return;

    // 元のウィジェットタイプと大きさを記録しておく
    if (!origProps[widget.name]) {
        origProps[widget.name] = { origType: widget.type, origComputeSize: widget.computeSize };
    }

    const origSize = node.size;

    // Set the widget type and computeSize based on the show flag
    widget.type = show ? origProps[widget.name].origType : HIDDEN_TAG + suffix;
    widget.computeSize = show ? origProps[widget.name].origComputeSize : () => [0, -4];

    // Recursively handle linked widgets if they exist
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, ":" + widget.name, show));

    // Calculate the new height for the node based on its computeSize method
    const newHeight = node.computeSize()[1];
    node.setSize([node.size[0], newHeight]);
}

/**
 * 番号付きウィジェットの表示・非表示切り替え
 */
function handleWidgetsVisibility(node, countValue, targets) {
    // 全てのウィジェットについて処理
    for (let i = 1; i <= 50; i++) {

        // 同じ番号が付いた関連ウィジェットを対象にする
        targets.forEach(target => {
            const widget = findWidgetByName(node, `${target}_${i}`);

            if (i <= countValue) {
                toggleWidget(node, widget, true);
            } else {
                toggleWidget(node, widget, false);
            }
        });
    }
}


export { sleep, findWidgetByName, findWidgetOrInputsByName, findWidgetByType, setCookie, getCookie, loadCssFile, handleWidgetsVisibility }