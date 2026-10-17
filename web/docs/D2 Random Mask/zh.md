# D2 Random Mask

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/random_mask.png">
</figure>

- 輸出隨機長方形遮罩的節點
- 長方形會被放置在不超出 `width` / `height` 的位置

## Input

- `width` / `height`
  - 輸出遮罩的尺寸
- `min_width` / `max_width`
  - 長方形寬度的範圍（像素）
- `min_height` / `max_height`
  - 長方形高度的範圍（像素）
- `seed`
  - 亂數種子。相同的值會得到相同的長方形

## Output

- `width` / `height`
  - 輸入的遮罩尺寸會原樣輸出
- `mask`
  - 長方形內側為白色的遮罩
- `mask_x` / `mask_y`
  - 長方形左上角的座標
- `mask_w` / `mask_h`
  - 長方形的寬度與高度

## 關於長方形的尺寸

`min_width` 與 `max_width` 填入相同的值時寬度會固定，只有位置隨機變動。

當 `max` 小於 `min` 時會互換處理，指定大於 `width` / `height` 的尺寸時則會縮小到遮罩的尺寸。長方形不會超出遮罩之外。
