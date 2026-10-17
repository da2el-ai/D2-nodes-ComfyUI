# D2 Random Point

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/random_point.png">
</figure>

- ランダムな XY 座標を出力するノード
- min / max を指定することで範囲を限定できる

## Input

- `width` / `height`
  - 座標系のサイズ
- `min_x` / `max_x`
  - X 座標の範囲
- `min_y` / `max_y`
  - Y 座標の範囲
- `mode`
  - `absolute`: 実際のピクセル座標を出力する
  - `relative`: 0.0〜1.0 の相対値を出力する
- `number_type`
  - `int` / `float`。`mode` が `absolute` のときだけ効く
- `seed`
  - 乱数の種。同じ値なら同じ座標になる

## Output

- `width` / `height`
  - 入力した座標系のサイズがそのまま出力される
- `x` / `y`
  - ランダムに決まった座標

## 範囲指定について

`min_x` `max_x` `min_y` `max_y` は、`mode` に関わらず常に 0.0〜1.0 の相対値で指定します。

たとえば `min_x` を `0.25`、`max_x` を `0.75` にすると、中央寄りの範囲だけに座標が出ます。`width` を変えても「中央寄り」という意味は変わりません。

`min` と `max` に同じ値を入れると、その位置に固定されます。

## number_type について

`mode` が `absolute` のとき、`int` なら `100` のような整数、`float` なら `100.3968` のような小数を出力します。

`relative` は0〜1の範囲なので常に小数です。
