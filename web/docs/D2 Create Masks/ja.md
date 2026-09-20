# D2 Create Masks

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/create_masks.png">
</figure>

- キャンバス上の長方形をドラッグして、複数のマスクを作るノード
- 長方形の内側をドラッグすると移動、四隅の白丸をドラッグするとリサイズできる
- 長方形は `mask_count` で増減し、出力 `mask_1` `mask_2` … も連動して増減する
- ノードに画像をドラッグ＆ドロップすると、キャンバスの背景に表示され `width` / `height` にも反映される

## Input

- `mask_count`
  - マスクの数（1〜16）。出力 `mask_N` の数と連動する
- `select_mask`
  - アクティブにするマスクの番号。キャンバスでクリックしたマスクの番号に自動で変わる
- `width` / `height`
  - 出力するマスクのサイズ。キャンバスのアスペクト比もこれで決まる
- `image`
  - 背景に表示する画像。空欄なら黒いキャンバスになる
- `masks`
  - マスクの位置とサイズの JSON。ドラッグすると自動で更新されるので、通常は触らなくてよい

## Output

- `image`
  - 指定した画像。画像を指定していない場合は `width` × `height` の黒画像
- `width` / `height`
  - マスクのサイズ
- `mask_1`
  - マスク1。`mask_count` が「3」なら `mask_2` `mask_3` も出力される

## アクティブなマスクについて

クリックしたマスクが「アクティブ」になり、いちばん手前に表示されて四隅にリサイズ用の白丸が出ます。

マスクが完全に重なっていると下のマスクをクリックできないので、そのときは `select_mask` で番号を選んでください。逆にクリックでアクティブを変えると `select_mask` も追従します。
