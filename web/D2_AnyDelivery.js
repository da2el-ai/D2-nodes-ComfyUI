import { app } from "/scripts/app.js";
import { findWidgetByName, findInputByName, findOutputByName } from "./modules/utils.js";

const THROW_LIST = ["_package", "_label", "_update"];
const INPUT_FIX = 3;
const OUTPUT_FIX = 1;


/**
 * 不要なinput/outputを削除
 */
const removeFromNode = (node, type, items, inputsOrOutputs) => {
    const removeList = [];

    for (let i = 0; i < inputsOrOutputs.length; i++) {
        const input = inputsOrOutputs[i];

        // 特定の名前は除外
        if(THROW_LIST.includes(input.name)) continue;

        // ラベルに同じ名前がなければ削除リストにindexを追加
        if(!items.includes(input.name)){
            removeList.push(i);
        }
    }

    // インデックスがずれないように逆順で削除
    removeList.sort((a, b) => b - a); // 降順ソート

    removeList.forEach(index => {
        if(type === "input"){
            node.removeInput(index);
        }else{
            node.removeOutput(index);
        }
    });
}

/**
 * 必要なinput/outputを追加
 */
const addToNode = (type, items, node) => {
    items.forEach(item => {
        // 既に存在しない場合のみ追加
        if(type === "input"){
            if (!findInputByName(node, item)) {
                node.addInput(item, "*");
            }
        }else{
            if (!findOutputByName(node, item)) {
                node.addOutput(item, "*");
            }
        }
    });

    if(type === "input"){
        // node.inputs を items の順番通りにする
        // 先頭3つは固定入力として保持
        if (node.inputs && node.inputs.length > INPUT_FIX) {
            // 固定部分を保持
            const fixedInputs = node.inputs.slice(0, INPUT_FIX);
            // 可変部分を取得
            const variableInputs = node.inputs.slice(INPUT_FIX);
            // 新しい順序の配列を作成
            const newOrder = [];
            
            // items の順序に従って新しい配列を構築
            // items に含まれる要素のみを追加
            items.forEach(itemName => {
                const input = variableInputs.find(input => input.name === itemName);
                if (input) {
                    newOrder.push(input);
                }
            });
            
            // node.inputs を固定部分と新しい順序の可変部分で置き換え
            node.inputs = [...fixedInputs, ...newOrder];
        }
    }else{
        // node.inputs を items の順番通りにする
        if (node.outputs && node.outputs.length > OUTPUT_FIX) {
            // 固定部分を保持
            const fixedOutputs = node.outputs.slice(0, OUTPUT_FIX);
            // 可変部分を取得
            const variableOutputs = node.outputs.slice(OUTPUT_FIX);
            // 新しい順序の配列を作成
            const newOrder = [];
            
            // items の順序に従って新しい配列を構築
            // items に含まれる要素のみを追加
            items.forEach(itemName => {
                const output = variableOutputs.find(output => output.name === itemName);
                if (output) {
                    newOrder.push(output);
                }
            });
            
            // node.outputs を固定部分と新しい順序の可変部分で置き換え
            node.outputs = [...fixedOutputs, ...newOrder];
        }
    }
}

const changeInputVisibility = (node, labelValue) => {
    console.log("////////////inputs", node.inputs);
    console.log("////////////outputs", node.outputs);
    const inputItems = [];
    const outputItems = [];

    // 必要な入出力をリストアップ
    labelValue.split(";").forEach(item => {
        const trimedItem = item.trim();

        if(trimedItem.startsWith('>')){
            inputItems.push(trimedItem.substring(1));
        }else if(trimedItem.startsWith('<')){
            outputItems.push(trimedItem.substring(1));
        }
    });
    console.log("inputItems", inputItems);
    console.log("outputItems", outputItems);

    // 不要なinput/outputを削除
    removeFromNode(node, "input", inputItems, node.inputs);
    removeFromNode(node, "output", outputItems, node.outputs);

    // 必要なinput/outputを追加
    addToNode("input", inputItems, node);
    addToNode("output", outputItems, node);

    // ノードの表示を更新
    node.setDirtyCanvas(true, true);
};

///////////////////////////
///////////////////////////
app.registerExtension({
    name: "Comfy.D2.D2_AnyDelivery",

    nodeCreated(node) {
        if (node.constructor.title !== "D2 Any Delivery") return;

        if (node.widgets) {
            const labeltWidget = findWidgetByName(node, "_label");
            let labelValue = labeltWidget.value;
            changeInputVisibility(node, labelValue);

            const btnWidget = findWidgetByName(node, "_update");
            btnWidget.callback = () => {
                let labelValue = labeltWidget.value;
                changeInputVisibility(node, labelValue);
            };
        }
    },

    // async beforeRegisterNodeDef(nodeType, nodeData, app) {
    //     if (nodeData.name !== "D2 Any Delivery") return;

    //     /**
    //      * ノード作成
    //      */
    //     const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    //     nodeType.prototype.onNodeCreated = function () {
    //         const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

    //         const labeltWidget = findWidgetByName(this, "label");
    //         console.log("//////labeltWidget", labeltWidget);
    //         let labelValue = labeltWidget.value;
    //         changeInputVisibility(this, labelValue);

    //         const btnWidget = findWidgetByName(this, "update");
    //         console.log("///////btnWidget", btnWidget);
    //         btnWidget.callback = () => {
    //             let labelValue = labeltWidget.value;
    //             changeInputVisibility(this, labelValue);
    //         };
    //         return r;
    //     };
    // }
});
