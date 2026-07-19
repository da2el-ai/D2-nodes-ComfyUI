import { app } from "/scripts/app.js";
import { findWidgetByName } from "./modules/utils.js";


app.registerExtension({
    name: "Comfy.D2.D2_TagReport",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Tag Report") return;

        /**
         * フォルダ内キャプションのタグ集計レポートを取得
         */
        const getTagReport = (folder, extension, includeSubfolders, orderBy, withoutCount) => {
            return new Promise(async (resolve) => {
                // folder / extension はスペースや記号を含むため encodeURIComponent する
                const url = `/D2/tag-report/get-tags?folder=${encodeURIComponent(folder)}&extension=${encodeURIComponent(extension)}&include_subfolders=${includeSubfolders}&order_by=${orderBy}&without_count=${withoutCount}`;
                const response = await fetch(url);
                const data = await response.json();
                resolve(data.report);
            });
        }

        /**
         * ノード作成された
         * ウィジェット登録と初期設定
         */
        const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = origOnNodeCreated ? origOnNodeCreated.apply(this) : undefined;

            const getTagsBtnWidget = findWidgetByName(this, "get_tags");
            const folderWidget = findWidgetByName(this, "folder");
            const includeSubfoldersWidget = findWidgetByName(this, "include_subfolders");
            const extensionWidget = findWidgetByName(this, "extension");
            const orderByWidget = findWidgetByName(this, "order_by");
            const withoutCountWidget = findWidgetByName(this, "without_count");
            const textWidget = findWidgetByName(this, "text");

            getTagsBtnWidget.name = "Get tags";
            getTagsBtnWidget.callback = async () => {
                const report = await getTagReport(
                    folderWidget.value,
                    extensionWidget.value,
                    includeSubfoldersWidget.value,
                    orderByWidget.value,
                    withoutCountWidget.value
                );
                textWidget.value = report;
            };

            return r;
        };
    },
});
