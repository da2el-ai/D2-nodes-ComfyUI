# D2 Random Mask

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/random_mask.png">
</figure>

- ランダムな長方形のマスクを出力するノード
- 長方形は `width` / `height` からはみ出さない位置に置かれる

## Input

- `width` / `height`
  - 出力するマスクのサイズ
- `min_width` / `max_width`
  - 長方形の幅の範囲（ピクセル）
- `min_height` / `max_height`
  - 長方形の高さの範囲（ピクセル）
- `seed`
  - 乱数の種。同じ値なら同じ長方形になる

## Output

- `width` / `height`
  - 入力したマスクのサイズがそのまま出力される
- `mask`
  - 長方形の内側が白いマスク
- `mask_x` / `mask_y`
  - 長方形の左上の座標
- `mask_w` / `mask_h`
  - 長方形の幅と高さ

## 長方形のサイズについて

`min_width` と `max_width` に同じ値を入れると幅が固定され、位置だけがランダムに動きます。

`min` より `max` が小さいときは入れ替えて扱い、`width` / `height` より大きいサイズを指定したときはマスクのサイズまで縮めます。長方形がマスクの外にはみ出すことはありません。
