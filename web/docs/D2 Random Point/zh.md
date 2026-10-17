# D2 Random Point

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/random_point.png">
</figure>

- 輸出隨機 XY 座標的節點
- 透過指定 min / max 可限定範圍

## Input

- `width` / `height`
  - 座標系的尺寸
- `min_x` / `max_x`
  - X 座標的範圍
- `min_y` / `max_y`
  - Y 座標的範圍
- `mode`
  - `absolute`: 輸出實際的像素座標
  - `relative`: 輸出 0.0〜1.0 的相對值
- `number_type`
  - `int` / `float`。僅在 `mode` 為 `absolute` 時有效
- `seed`
  - 亂數種子。相同的值會得到相同的座標

## Output

- `width` / `height`
  - 輸入的座標系尺寸會原樣輸出
- `x` / `y`
  - 隨機決定的座標

## 關於範圍指定

`min_x` `max_x` `min_y` `max_y` 無論 `mode` 為何，一律以 0.0〜1.0 的相對值指定。

例如將 `min_x` 設為 `0.25`、`max_x` 設為 `0.75`，座標就只會出現在偏中央的範圍。即使變更 `width`，「偏中央」的意義也不會改變。

`min` 與 `max` 填入相同的值時，會固定在該位置。

## 關於 number_type

`mode` 為 `absolute` 時，`int` 會輸出如 `100` 的整數，`float` 會輸出如 `100.3968` 的小數。

`relative` 為 0〜1 的範圍，因此一律為小數。
