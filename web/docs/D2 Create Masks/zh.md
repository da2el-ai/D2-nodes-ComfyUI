# D2 Create Masks

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/create_masks.png">
</figure>

- 透過在畫布上拖曳長方形來建立多個遮罩的節點
- 拖曳長方形內側可移動，拖曳四角的白色圓點可調整大小
- 長方形會依 `mask_count` 增減，輸出 `mask_1` `mask_2` … 也會連動增減
- 將圖像拖放到節點上，就會顯示在畫布背景，並套用其尺寸到 `width` / `height`

## Input

- `mask_count`
  - 遮罩的數量（1〜16）。輸出 `mask_N` 的數量會與此連動
- `select_mask`
  - 要設為作用中的遮罩編號。在畫布上點擊遮罩時會自動變更為該遮罩的編號
- `width` / `height`
  - 輸出遮罩的尺寸。畫布的長寬比也由此決定
- `image`
  - 顯示於背景的圖像。留空則為黑色畫布
- `masks`
  - 遮罩位置與尺寸的 JSON。拖曳時會自動更新，通常不需要修改

## Output

- `image`
  - 指定的圖像。未指定圖像時為 `width` × `height` 的黑色圖像
- `width` / `height`
  - 遮罩的尺寸
- `mask_1`
  - 遮罩1。若 `mask_count` 為「3」，也會輸出 `mask_2` `mask_3`

## 關於作用中的遮罩

點擊的遮罩會成為「作用中」，顯示在最前方，並在四角出現用於調整大小的白色圓點。

當遮罩完全重疊時無法點擊下層的遮罩，此時請用 `select_mask` 選擇編號。反之，透過點擊變更作用中的遮罩時，`select_mask` 也會跟著更新。
