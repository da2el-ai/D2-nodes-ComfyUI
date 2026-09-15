import { app } from "/scripts/app.js";
import { findWidgetByName } from "./modules/utils.js";


app.registerExtension({
    name: "Comfy.D2.D2_TagReport",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "D2 Tag Report") return;

        /**
         * フォルダ内キャプションのタグ集計レポートを取得
         * exclude_tags（タグ辞書）は数MBになりうるので POST ボディで送る
         */
        const getTagReport = (params) => {
            return new Promise(async (resolve) => {
                const response = await fetch("/D2/tag-report/get-tags", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(params),
                });
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
            const excludeTagsWidget = findWidgetByName(this, "exclude_tags");
            const textWidget = findWidgetByName(this, "text");

            getTagsBtnWidget.name = "Get tags";
            getTagsBtnWidget.callback = async () => {
                const report = await getTagReport({
                    folder: folderWidget.value,
                    extension: extensionWidget.value,
                    include_subfolders: includeSubfoldersWidget.value,
                    order_by: orderByWidget.value,
                    without_count: withoutCountWidget.value,
                    // ウィジェットの値のみ対応（他ノードから接続された値は取得できない）
                    exclude_tags: excludeTagsWidget?.value ?? "",
                });
                textWidget.value = report;
            };

            return r;
        };
    },
});
