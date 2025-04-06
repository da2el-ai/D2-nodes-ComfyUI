/**
 * 指定ミリ秒待機
 */
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * ウィジェットを名前から探す
 */
const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

/**
 * 入力を名前から探す
 */
const findInputByName = (node, name) => {
    return node.inputs ? node.inputs.find((w) => w.name === name) : null;
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
};

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
};

/**
 * CSSを動的に読み込む
 */
const loadCssFile = (filePath) => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = filePath;
    document.head.appendChild(link);
};

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
    widget.linkedWidgets?.forEach((w) => toggleWidget(node, w, ":" + widget.name, show));

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
        targets.forEach((target) => {
            const widget = findWidgetByName(node, `${target}_${i}`);

            if (i <= countValue) {
                toggleWidget(node, widget, true);
            } else {
                toggleWidget(node, widget, false);
            }
        });
    }
}


/**
 * 番号付き入力の追加・削除
 * params = [{name:`input名`, type:`input型`}]
 */
function handleInputsVisibility(node, countValue, params) {
    const inputsToRemove = [];
    // 削除対象のインデックスをリストアップ
    for (let i = 0; i < node.inputs.length; i++) {
        const input = node.inputs[i];
        // params に定義されたプレフィックスで始まるかチェック
        const paramMatch = params.find(p => input.name.startsWith(p.name + "_"));
        if (paramMatch) {
            // 末尾の番号を取得
            const match = input.name.match(/_(\d+)$/);
            if (match) {
                const index = parseInt(match[1], 10);
                // 番号が countValue より大きい場合は削除対象
                if (index > countValue) {
                    inputsToRemove.push(i);
                }
            }
        }
    }

    // インデックスがずれないように逆順で削除
    inputsToRemove.sort((a, b) => b - a); // 降順ソート
    inputsToRemove.forEach(index => {
        node.removeInput(index);
    });

    // 必要な入力がなければ追加
    for (let i = 1; i <= countValue; i++) {
        params.forEach((param) => {
            const name = `${param.name}_${i}`;
            // 既に存在しない場合のみ追加
            if (!findInputByName(node, name)) {
                node.addInput(name, param.type);
            }
        });
    }
    // ノードの表示を更新
    node.setDirtyCanvas(true, true);
}


/**
 * 表示線用ウィジェットのベース
 */
function getReadOnlyWidgetBase(node, type, inputName, value) {
    return {
        type: type,
        name: inputName,
        value: value,
        size: [100, 30],

        // 描画処理
        draw(ctx, node, width, y) {
            // 背景描画
            ctx.fillStyle = "#2a2a2a";
            ctx.fillRect(0, y, width, this.size[1]);

            // データ表示
            ctx.fillStyle = "#ffffff";
            ctx.font = "12px Arial";
            // ctx.fillText(JSON.stringify(text), 10, y + 20);
            ctx.fillText("sample", 20, y + 20);
        },

        // サイズ計算
        computeSize(width) {
            return [Math.min(width, this.size[0]), this.size[1]];
        },

        // データのシリアライズ
        async serializeValue(nodeId, widgetIndex) {
            return this.value;
        },

        // データ更新メソッド
        setValue(value) {
            this.value = value;
            node.setDirtyCanvas(true); // 再描画をトリガー
        },
    };
}

export {
    sleep,
    findWidgetByName,
    findWidgetOrInputsByName,
    findWidgetByType,
    findInputByName,
    setCookie,
    getCookie,
    loadCssFile,
    handleWidgetsVisibility,
    handleInputsVisibility,
    getReadOnlyWidgetBase,
};
