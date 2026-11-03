<h1 style="border:none;">
<img src="./docs/img/title.jpg" style="max-width:100%">
</h1>



<a href="docs/en/index.md">English</a> | <a href="docs/ja/index.md">日本語</a> | <a href="docs/zh/index.md">繁体中文</a>



<strong>D2 Nodes ComfyUI</strong> is a collection of custom nodes created with the themes of "slightly convenient," "simple," and "maintaining versatility."
Features:

- Versatile XY Plot
- Workflow that automatically switches quality tags based on Checkpoint lineage
- Queue button with freely adjustable batch sizes
- Various other "slightly convenient nodes"

**⚠️ ＜注意 / Notice＞ 2026.11.04 ⚠️**

Version 43.0.0 で、ComfyUI 標準の Start Loop / End Loop に対応するため、多数のノードの入出力の名前・型・並び順を変更しました。
古いワークフローでは接続が外れたり、別の出力につながったりするので、ノードを再接続してください。

- 名称変更：`LIST` → `ARRAY`（ComfyUI 標準の Array 型）
- 名称変更：`BATCH` → `LIST`（ComfyUI 本来の LIST 出力）
- 名称変更：`x / y_list` / `x_list` / `y_list` → `x / y_items` / `x_items` / `y_items`
- 非推奨：`D2 List To String` / `D2 XY List To Plot` は非推奨になりました。今後は `D2 List Converter` をお使いください。

In version 43.0.0, the names, types and order of inputs/outputs of many nodes have changed to support ComfyUI's built-in Start Loop / End Loop.
Links in older workflows may be disconnected or attached to a different output, so please reconnect the nodes.

- Renamed: `LIST` → `ARRAY` (ComfyUI's built-in Array type)
- Renamed: `BATCH` → `LIST` (ComfyUI's native LIST output)
- Renamed: `x / y_list` / `x_list` / `y_list` → `x / y_items` / `x_items` / `y_items`
- Deprecated: `D2 List To String` / `D2 XY List To Plot` are deprecated. Please use `D2 List Converter` instead.

自 43.0.0 版起，為了支援 ComfyUI 內建的 Start Loop / End Loop，變更了許多節點輸入/輸出的名稱、型別與順序。
舊的工作流程中，連線可能會中斷或接到其他輸出，請重新連接節點。

- 名稱變更：`LIST` → `ARRAY`（ComfyUI 內建的 Array 型別）
- 名稱變更：`BATCH` → `LIST`（ComfyUI 原生的 LIST 輸出）
- 名稱變更：`x / y_list` / `x_list` / `y_list` → `x / y_items` / `x_items` / `y_items`
- 不建議使用：`D2 List To String` / `D2 XY List To Plot` 已不建議使用，今後請改用 `D2 List Converter`。

**⚠️ ＜注意 / Notice＞ 2026.01.15 ⚠️**

Version 32.0.0 から ComfyUI V3 Scheme に移行しました。
古いバージョンのComfyUIで動作しない場合は Ver32.0.0より前のバージョンをお使いください。

Starting from version 32.0.0, this project has migrated to the ComfyUI V3 schema.
If it does not work on an older version of ComfyUI, please use a version earlier than v32.0.0.

自 32.0.0 版起，本專案已遷移至 ComfyUI V3 Scheme。
若在舊版 ComfyUI 上無法運作，請改用 32.0.0 之前的版本。

