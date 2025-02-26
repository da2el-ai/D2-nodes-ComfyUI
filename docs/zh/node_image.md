<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>




# Node


## :tomato: Image Node


### D2 預覽圖像

<figure>
<img src="../img/preview_image_1.png">
<img src="../img/preview_image_2.png">
</figure>

- 點擊 `Popup Image` 按鈕可顯示全螢幕圖庫

---


### D2 Load Image

<figure>
<img src="../img/load_image.png">
</figure>

- 可從圖像獲取提示詞的 Load Image 節點
- 支援 `StableDiffusion webui A1111`、`NovelAI` 創建的圖像
- 附帶打開遮罩編輯器按鈕

#### Input

- `image_path`
  - 輸入圖像路徑即可載入文件
  - 用於連接 `D2 Folder Image Queue`

#### Output

- `IMAGE / MASK`
    - 圖像和遮罩
- `width / height`
    - 圖像尺寸
- `positive` / `negative`
    - 提示詞

※根據工作流程配置，可能無法獲取提示詞。例如，如果沒有包含「KSampler」字樣的節點（如：Tiled KSampler），則無法獲取。

---

### D2 Load Folder Images

<figure>
<img src="../img/load_folder_images.png">
</figure>

- 批量載入並輸出資料夾內的圖像
- 用於 `D2 Grid Image` 等
- 如需順序處理請使用 `D2 Folder Image Queue`

#### Input

- `folder`
  - 指定資料夾完整路徑
- `extension`
  - 如僅載入 JPEG 圖像則指定為 `*.jpg`
  - 也可使用 `*silver*.webp` 等指定方式

---

### D2 Folder Image Queue

<figure>
<img src="../img/folder_image_queue_2.png">
</figure>

- 輸出資料夾內圖像的路徑
- 執行 Queue 時會自動執行與圖像數量相應的 Queue

#### Input

- `folder`
  - 圖像資料夾
- `extension`
  - 指定文件名過濾器
  - `*.*`: 所有圖像
  - `*.png`: 僅 PNG 格式
- `start_at`
  - 開始處理的圖像編號
- `auto_queue`
  - `true`: 自動執行剩餘的 Queue
  - `false`: 僅執行一次

#### Output

- `image_path`
  - 圖像完整路徑

---

### D2 Grid Image

<figure>
<img src="../img/grid_image.png">
</figure>

- 輸出網格圖像
- 支持水平和垂直排列

#### Input

- `max_columns`
  - 水平排列的圖片數量
  - 當 `swap_dimensions` 為 `true` 時，則為垂直排列的數量
- `grid_gap`
  - 圖片之間的間距
- `swap_dimensions`
  - `true`: 垂直排列
  - `false`: 水平排列
- `trigger_count`
  - 當輸入圖片達到指定數量時輸出網格圖像
- `Image count`
  - 輸入圖片的數量
- `Reset Images`
  - 清除所有輸入的圖片

---

### D2 Image Stack

<figure>
<img src="../img/image_stack.png">
</figure>

- 將輸入的多個圖像一起輸出
- 最多可輸入 50 個

#### Input

- `image_count`
  - 可增減輸入數量，最多 50 個

---

### D2 EmptyImage Alpha

<figure>
<img src="../img/empty_image_alpha.png">
</figure>

- 為 EmptyImage 添加 α 通道（透明度）
