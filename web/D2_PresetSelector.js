import { app } from "/scripts/app.js";
import { findWidgetByName, findOutputByName } from "./modules/utils.js";

const SUPPORTED_TYPES = ["INT", "FLOAT", "STRING", "BOOLEAN"];

/**
 * preset_text を解析する
 * 成功時: { names, types, presets:[{title, values}] }
 * 失敗時: { error: メッセージ }
 */
const parsePresetText = (text) => {
    const lines = text.split("\n").map((l) => l.trim()).filter((l) => l !== "");

    if (lines.length < 3) {
        return { error: "行数が不足しています（1行目=出力名、2行目=型、3行目以降=プリセットが必要です）" };
    }

    const names = lines[0].split(";").map((s) => s.trim());
    const types = lines[1].split(";").map((s) => s.trim());

    if (names.length !== types.length) {
        return { error: `出力名(${names.length}個)と型(${types.length}個)の数が一致しません` };
    }

    const badType = types.find((t) => !SUPPORTED_TYPES.includes(t));
    if (badType) {
        return { error: `未サポートの型です: '${badType}'（${SUPPORTED_TYPES.join(" / ")} のいずれかにしてください）` };
    }

    const presets = [];
    for (const line of lines.slice(2)) {
        const cells = line.split(";").map((s) => s.trim());
        const title = cells[0];
        const values = cells.slice(1);
        if (values.length !== names.length) {
            return { error: `プリセット '${title}' の値の数(${values.length})が出力数(${names.length})と一致しません` };
        }
        presets.push({ title, values });
    }

    return { names, types, presets };
};

/**
 * output スロットを names に合わせて再構築する（固定出力なし / OUTPUT_FIX = 0）
 */
const rebuildOutputs = (node, names) => {
    // names に無い output を削除（インデックスがずれないよう逆順）
    const removeList = [];
    for (let i = 0; i < node.outputs.length; i++) {
        if (!names.includes(node.outputs[i].name)) {
            removeList.push(i);
        }
    }
    removeList.sort((a, b) => b - a);
    removeList.forEach((index) => node.removeOutput(index));

    // 不足している output を追加（AnyType *）
    names.forEach((name) => {
        if (!findOutputByName(node, name)) {
            node.addOutput(name, "*");
        }
    });

    // names の順番通りに整列
    const newOrder = [];
    names.forEach((name) => {
        const output = node.outputs.find((o) => o.name === name);
        if (output) newOrder.push(output);
    });
    node.outputs = newOrder;
};

/**
 * preset_text から現在のプリセットタイトル一覧を返す（書式エラー時は空配列）
 */
const getPresetTitles = (node) => {
    const textWidget = findWidgetByName(node, "preset_text");
    const parsed = parsePresetText(textWidget ? textWidget.value || "" : "");
    return parsed.error ? [] : parsed.presets.map((p) => p.title);
};

/**
 * preset プルダウンの選択肢を「関数（getter）」として設定する。
 * options.values を関数にすると、ドロップダウン表示・Primitive ノード接続・
 * サブグラフ入力・ワークフロー復元のいずれでも、その時点の preset_text から
 * 常に最新の選択肢が得られる（静的配列だと復元タイミングで空のまま固定されてしまう）。
 * ※ 選択中の値（widget.value）はここでは触らない＝復元を妨げない
 */
const setupPresetCombo = (node) => {
    const widget = findWidgetByName(node, "preset");
    if (!widget) return;
    widget.options = widget.options || {};
    widget.options.values = () => getPresetTitles(node);
};

/**
 * preset_text を解析して output スロットを再構築する（_update ボタン用）
 * showAlert: true なら書式エラー時に window.alert で警告する
 * 書式エラー時はスロットを再構築せず、直前の状態を維持する
 */
const updateNode = (node, { showAlert = false } = {}) => {
    const textWidget = findWidgetByName(node, "preset_text");
    if (!textWidget) return;

    const text = textWidget.value || "";

    // 完全に空のときは初期状態として何もしない（警告も出さない）
    if (text.trim() === "") return;

    const parsed = parsePresetText(text);

    if (parsed.error) {
        if (showAlert) {
            window.alert(`D2 Preset Selector\n\n${parsed.error}`);
        }
        return;
    }

    rebuildOutputs(node, parsed.names);

    // 選択中の値が新しい選択肢に無ければ先頭へフォールバック（選択肢は getter で動的取得）
    const titles = parsed.presets.map((p) => p.title);
    const presetWidget = findWidgetByName(node, "preset");
    if (presetWidget && !titles.includes(presetWidget.value)) {
        presetWidget.value = titles.length > 0 ? titles[0] : "";
    }

    node.setDirtyCanvas(true, true);
};

app.registerExtension({
    name: "Comfy.D2.D2_PresetSelector",

    nodeCreated(node) {
        if (node.constructor.title !== "D2 Preset Selector") return;
        if (!node.widgets) return;

        // プルダウンの選択肢を getter 化（値には触れないので復元を妨げない）
        setupPresetCombo(node);

        // 復元時の output 再構築（preset_text が既にあれば反映。空ならスキップ）
        updateNode(node);

        const btnWidget = findWidgetByName(node, "_update");
        if (btnWidget) {
            btnWidget.callback = () => updateNode(node, { showAlert: true });
        }
    },
});
