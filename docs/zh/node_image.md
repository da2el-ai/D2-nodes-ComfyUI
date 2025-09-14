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

### D2 Save Image

<figure>
  <img src="../img/save_image_2.png?2">
  <figcaption>▲filenames 輸出保存圖像的路徑</figcaption>
</figure>

- 與 `D2 Preview Image` 相同，搭載全螢幕圖庫功能的圖像保存節點
- 支援 PNG / JPEG / WEBP / 動畫WEBP 圖像格式
- 在元數據中保存 A1111 風格的生成參數（僅 PNG / JPEG / WEBP 格式）
- 使用 `D2 Load Image` 載入時可以提取保存圖像中的 positive、negative 提示詞（僅 PNG / JPEG / WEBP 格式）

<figure>
  <img src="../img/save_image_3.png?2">
  <figcaption>▲從 d2_pipe 獲取生成參數並保存到元數據</figcaption>
</figure>

#### Input

- `images`: 要保存的圖像
- `d2_pipe`: 從 `D2 KSampler` 等接收生成參數
- `filename_prefix`: 檔案名格式。詳情請參閱 <a href="node_text.md#D2-Filename-Template">`D2 Filename Template`</a>
- `preview_only`:
  - `true`: 僅顯示預覽，不保存圖像
  - `false`: 保存圖像
- `format`: 從 `png` / `jpeg` / `webp` / `animated_webp` 中選擇圖像格式
- `lossless`: 適用於 `webp` 和 `animated_webp`
  - `true`: 無損壓縮
  - `false`: 有損壓縮
- `quality`: 圖像壓縮率。適用於 `jpeg` 或 `webp`、`animated_webp` 且 `lossless:false` 時
- `fps`: `animated_webp` 的幀率
- `Popup Image`: 點擊按鈕時顯示全螢幕圖庫

#### Output

- `filenames`: 保存的圖像文件完整路徑陣列

---

### D2 Save Image Eagle

<figure>
  <img src="../img/save_image_eagle.png?2">
</figure>

- 具有Eagle註冊功能的 `D2 Save Image`
- <a href="https://eagle.cool/" target="_blank">Eagle官方網站</a>

#### 與 `D2 Send Eagle` 的區別

- 支援動畫WEBP
- 全螢幕圖庫功能
- 檔案名規則符合標準 `Save Image`
- 排除了標籤保存功能

#### Input

- `eagle_folder`: Eagle註冊資料夾。可以使用資料夾名稱或資料夾ID
- `memo_text`: 在Eagle中註冊為備忘錄的文本

#### 在Eagle備忘錄中記錄A1111 webui風格的參數

##### 自動創建

當從 `D2 KSampler` 連接 `d2_pipe` 時，會自動保存到Eagle備忘錄。

<figure>
  <img src="../img/save_image_eagle_4.png?2">
</figure>

##### 自定義格式創建

對於視頻等複雜的生成參數，也可以記錄自定義備忘錄。

<figure>
  <img src="../img/save_image_eagle_3.png?2">
</figure>

#### Input

- `eagle_folder`: Eagle註冊資料夾。可以使用資料夾名稱或資料夾ID
- `memo_text`: 在Eagle中註冊為備忘錄的文本

#### 在Eagle備忘錄中記錄A1111 webui風格的參數

<figure>
<img src="../img/save_image_eagle_3.png?2">
</figure>

使用 `D2 Filename Template2` 創建模板，並將其輸入到 `D2 Save Image Eagle` 的 `memo_text` 中。

在上面的示例中，`D2 KSampler` 的 `positive` 和 `negative` 被輸入到 `arg_1` 和 `arg_2` 並通過 `%arg_1%` 和 `%arg_2%` 獲取，而其他參數則通過 `%{Node name}.{Param}` 獲取。

有關參數獲取方法的詳細信息，請參閱 <a href="node_text.md#D2-Filename-Template">`D2 Filename Template`</a>。

```
%arg_1%

Negative prompt: %arg_2%
Steps: %D2 KSampler.steps%, Sampler: %D2 KSampler.sampler_name% %D2 KSampler.scheduler%, CFG scale: %D2 KSampler.cfg%, Seed: %D2 KSampler.seed%, Size: %Empty Latent Image.width%x%Empty Latent Image.height%, Model: %D2 Checkpoint Loader.ckpt_name%
```
輸出結果
```
masterpiece, 1girl, bikini, blue sky,

Negative prompt: bad quality, worst quality, sepia,
Steps: 20, Sampler: euler_ancestral simple, CFG scale: 5.000000000000001, Seed: 926243299419009, Size: 768x1024, Model: _SDXL_Illustrious\anime\HiyokoDarkness_vpred_v2_20250329.safetensors
```

---

### D2 Send File Eagle

<figure>
<img src="../img/send_file_eagle.png?2">
</figure>

- 將 `file_path` 輸入的路徑文件註冊到 <a href="https://eagle.cool/" target="_blank">Eagle</a>
- 為了將 `Video Combine` 的輸出文件註冊到Eagle而創建
- 通過使用 `D2 File Template2` 輸入 `memo_text` 也可以保存視頻生成參數

##### 關於 file_path

以字符串或字符串數組的形式提供文件的完整路徑。

例：字符串
```
D:\ComfyUI\output\foo.png
```
例：字符串數組
```
["D:\ComfyUI\output\foo.png","D:\ComfyUI\output\bar.png"]
```

##### 關於 Video Combine 輸出的 Filenames

<a href="https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite" target="_blank">Video Combine</a> 輸出的 `Filenames` 是如下形式的數組：

```
[
  true, 
  [
    "D:\\ComfyUI\\output\\AnimateDiff_00002.png",
    "D:\\ComfyUI\\output\\AnimateDiff_00002.mp4"
  ]
]
```

在上圖中，使用了 <a href="https://github.com/godmt/ComfyUI-List-Utils" target="_blank">ComfyUI-List-Utils</a> 中的 `Exec` 節點來提取文件名部分。



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

- `IMAGE / MASK`: 圖像和遮罩
- `width / height`: 圖像尺寸
- `positive` / `negative`: 提示詞
- `filename` / `filepath`: 保存文件的名稱和路徑
- `pnginfo`: 圖像元數據

#### 關於提示詞輸出

支援以下節點和UI保存的圖像：

- `D2 Save Image`、`D2 Save Image Eagle`
- <a href="https://github.com/easygoing0114/ComfyUI-easygoing-nodes?tab=readme-ov-file" target="_blank">Save Image With Prompt</a>
- <a href="https://github.com/giriss/comfy-image-saver" target="_blank">Save Image w/Metadata</a>
- Novel AI
- A1111（包括Forge系列）

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

- 將多個輸入圖像合併為一個批次
- 可與 D2 Grid Image 等一起使用
- 最多支持50個輸入


---

### D2 Image Mask Stack

<figure>
<img src="../img/image_mask_stack.png">
</figure>

- 將多個輸入圖像和遮罩合併為一個批次
- 基本上是 D2 Image Stack 加上遮罩支持功能


---

### D2 EmptyImage Alpha

<figure>
<img src="../img/empty_image_alpha.png">
</figure>

- 為 EmptyImage 添加 α 通道（透明度）


---


### D2 Mosaic Filter

<figure>
<img src="../img/mosaic.png">
</figure>

- 添加馬賽克濾鏡效果
- 可調整透明度、亮度和顏色反轉等設置


---


### D2 Cut By Mask

<figure>
<img src="../img/cut-by-mask.png">
</figure>

- 使用遮罩裁剪圖像
- 可以指定輸出形狀、尺寸、邊距等


#### Input

- `images`: 要裁剪的原始圖像
- `mask`: 遮罩
- `cut_type`: 裁剪圖像的形狀
    - `mask`: 按照遮罩形狀裁剪
    - `rectangle`: 從遮罩形狀計算並裁剪出矩形
    - `square_thumb`: 以最大尺寸的正方形進行裁剪。適用於縮略圖的模式
- `output_size`: 輸出圖像尺寸
    - `mask_size`: 遮罩尺寸
    - `image_size`: 輸入圖像尺寸（保持輸入圖像位置的同時周圍變為透明）
- `square_thumb`: 以最大尺寸的正方形進行裁剪。適用於縮略圖的模式
- `padding`: 擴展遮罩area的像素數（預設值 0）
- `min_width`: 遮罩尺寸的最小寬度（預設值 0）
- `min_height`: 遮罩尺寸的最小高度（預設值 0）
- `output_alpha`: 是否在輸出圖像中包含透明度通道

#### output
- `image`: 通過遮罩區域裁剪的圖像
- `mask`: 遮罩
- `rect`: 裁剪的矩形區域



---


### D2 Paste By Mask

<figure>
<img src="../img/paste-by-mask.png">
</figure>

- 使用由 D2 Paste By Mask 創建的遮罩或矩形區域合成圖像
- 可以指定模糊寬度、貼上形狀等

#### Input

- `img_base`: 底層圖像（支援批次處理）
- `img_paste`: 要貼上的圖像（支援批次處理）
- `paste_mode`: 決定如何裁剪 img_paste 以及貼上座標
    - `mask`: 用 mask_opt 遮罩 img_paste 並在位置 x=0, y=0 貼上（遮罩形狀貼上）
    - `rect_full`: 將 img_paste 裁剪為 rect_opt 的尺寸並在 rect_opt 位置貼上（矩形貼上）
    - `rect_position`: 在 rect_opt 位置貼上 img_paste（矩形貼上）
    - `rect_pos_mask`: 用 mask_opt 遮罩 img_paste 並在 rect_opt 位置貼上（遮罩形狀貼上）
- `multi_mode`: 當 img_base、img_paste 其中一個或兩者都有多張圖像時的處理方式
    - `pair_last`: 從頭開始以相同索引處理 img_base 和 img_paste 對。如果其中一個圖像較少，則使用最後一張圖像
    - `pair_only`: 與 pair_last 相同。如果其中一個圖像較少，則在處理前顯示錯誤並停止
    - `cross`: 處理所有組合

input `optional`:
- `mask_opt`: 遮罩
- `rect_opt`: 矩形區域
- `feather`: 邊緣模糊的像素數（預設值 0）


#### output

- `image`: 合成的圖像

#### 關於 multi_mode

`pair_last` 和 `pair_only` 將 `img_base` 和 `img_paste` 中相同順序的圖像作為一對輸出。

<figure>
<img src="../img/paste-by-mask_pair.png">
</figure>

`cross` 輸出所有組合。

<figure>
<img src="../img/paste-by-mask_cross.png">
</figure>
