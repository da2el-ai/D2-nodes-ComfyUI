<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>




# D2 Nodes ComfyUI

**D2 Nodes ComfyUI** 是一個以「稍微方便」、「簡單」、「不失通用性」為主題開發的自定義節點集合。

- 高通用性的 XY Plot
- 根據 Checkpoint 系列自動切換品質標籤的工作流程
- 可自由設定生成數量的 Queue 按鈕
- 其他各種「稍微方便的節點」

## :exclamation: 注意

### 不需要的自定義節點
如果您已安裝以下自定義節點，請將其刪除：

- `ComfyUI-d2-size-selector`
- `ComfyUI-d2-steps`
- `ComfyUI-d2-xyplot-utils`

## :tomato: 節點

- <a href="node.md#d2-ksampler--d2-ksampleradvanced">`D2 KSampler / D2 KSampler(Advanced)`</a>
  - 可以用 STRING 格式輸入輸出提示詞的 KSampler
- <a href="node.md#d2-pipe">`D2 Pipe`</a>
  - 用於修改和獲取 D2 XYPlot Easy、D2 KSampler 和 D2 Send Eagle 所使用的 d2_pipe 的節點

### 載入器

- <a href="node.md#D2-Checkpoint-Loader">`D2 Checkpoint Loader`</a>
  - 輸出模型文件完整路徑的 Checkpoint Loader
- <a href="node.md#D2-Controlnet-Loader">`D2 Controlnet Loader`</a>
  - 連接到 `D2 KSampler` 可建立簡單工作流程的 Controlnet Loader
- <a href="node.md#D2-Load-Lora">`D2 Load Lora`</a>
  - 可通過文本指定的 Lora 加載器


### 尺寸

- <a href="node.md#D2-Get-Image-Size">`D2 Get Image Size`</a>
  - 顯示和獲取圖像尺寸
- <a href="node.md#D2-Size-Slector">`D2 Size Selector`</a>
  - 可從預設選擇圖像尺寸、Empty latent 輸出節點
  - 可從圖像獲取尺寸
- <a href="node.md#D2-Image-Resize">`D2 Image Resize`</a>
  - 可指定到小數點後 3 位的圖像縮放
  - 可選擇四捨五入、無條件捨去、無條件進位
- <a href="node.md#D2-Resize-Calculator">`D2 Resize Calculator`</a>
  - 計算結果必定為 8 的倍數的圖像尺寸計算節點
  - 可選擇四捨五入、無條件捨去、無條件進位

### Refiner
- <a href="node.md#D2-Refiner-Steps">`D2 Refiner Steps`</a>
  - 輸出用於 Refiner 的步數
- <a href="node.md#D2-Refiner-Steps-A1111">`D2 Refiner Steps A1111`</a>
  - 用於 img2img 的 Refiner，可指定 denoise
- <a href="node.md#D2-Refiner-Steps-Tester">`D2 Refiner Steps Tester`</a>
  - 用於確認步數的節點

### Merge Node

- <a href="node.md#D2-Model-and-CLIP-Merge-SDXL">`D2 Model and CLIP Merge SDXL`</a>
  - 將 ModelMergeSDXL 和 CLIPMergeSimple 結合的節點


### 文字

- <a href="node_text.md#D2-Regex-Replace">`D2 Regex Replace`</a>
  - 可設定多個條件的文字替換節點
- <a href="node_text.md#D2-Regex-Switcher">`D2 Regex Switcher`</a>
  - 根據輸入文字切換輸出文字的節點
  - 可進行字串連接
- <a href="node_text.md#D2-Multi-Output">`D2 Multi Output`</a>
  - 以列表形式輸出 SEED / STRING / INT / FLOAT
- <a href="node_text.md#D2-List-To-String">`D2 List To String`</a>
  - 將陣列轉換為字串
- <a href="node_text.md#D2-Filename-Template">`D2 Filename Template`</a>
  - 生成文件名稱
- <a href="node_text.md#D2-Token-Counter">`D2 Token Counter`</a>
  - 計算提示詞的標記數量
- <a href="node_text.md#D2-Prompt">`D2 Prompt`</a>
  - 具有刪除註解功能和顯示令牌數量的文字節點




### 圖像

- <a href="node_image.md#D2-Preview-Image">`D2 Preview Image`</a>
  - 具備圖庫功能的圖像預覽
- <a href="node_image.md#D2-Save-Image">`D2 Save Image`</a>
  - 具備圖庫功能的圖像保存
- <a href="node_image.md#D2-Save-Image-Eagle">`D2 Save Image Eagle`</a>
  - 具有Eagle註冊功能的 `D2 Save Image`
- <a href="node_image.md#D2-Send-File-Eagle">`D2 Send File Eagle`</a>
  - 將指定路徑的文件註冊到Eagle
- <a href="node_image.md#D2-Load-Image">`D2 Load Image`</a>
  - 可從圖像獲取提示詞的 Load Image
  - 支援 `StableDiffusion webui A1111`、`NovelAI` 創建的圖像
  - 附帶打開遮罩編輯器按鈕
- <a href="node_image.md#D2-Load-Folder-Images">`D2 Load Folder Images`</a>
  - 載入資料夾內的所有圖像
- <a href="node_image.md#D2-Folder-Image-Queue">`D2 Folder Image Queue`</a>
  - 依序輸出資料夾內的圖像路徑
  - 自動執行與圖像數量相應的佇列
- <a href="node_image.md#D2-Grid-Image">`D2 Grid Image`</a>
  - 生成網格圖像
- <a href="node_image.md#D2-Image-Stack">`D2 Image Stack`</a>
  - 將多個圖像合併為一個批次
- <a href="node_image.md#D2-Image-Mask-Stack">`D2 Image Mask Stack`</a>
  - 將多個圖像和遮罩合併為一個批次
- <a href="node_image.md#D2-EmptyImage-Alpha">`D2 EmptyImage Alpha`</a>
  - 輸出帶有 α 通道（透明度）的 EmptyImage
- <a href="node_image.md#D2-Mosaic-Filter">`D2 Mosaic Filter`</a>
  - 為圖像添加馬賽克濾鏡效果
- <a href="node_image.md#D2-Cut-By-Mask">`D2 Cut By Mask`</a>
  - 使用遮罩裁剪圖像
- <a href="node_image.md#D2-Paste-By-Mask">`D2 Paste By Mask`</a>
  - 使用遮罩貼上圖像


### XY Plot

- <a href="node_xy.md#D2-XY-Plot-Easy">`D2 XY Plot Easy`</a>
  - 限定於 D2 KSampler 項目的簡化版 XY Plot 節點，提供更簡潔的工作流程
- <a href="node_xy.md#D2-XY-Plot">`D2 XY Plot`</a>
  - 通用的 XY Plot 節點
  - 自動執行所需次數的佇列
- <a href="node_xy.md#D2-XY-Grid-Image">`D2 XY Grid Image`</a>
  - 生成網格圖像的節點
- <a href="node_xy.md#D2-XY-Prompt-SR">`D2 XY Prompt SR`</a>
  - 搜索替換文字並以列表返回，放在 `D2 XY Plot` 前的類型
- <a href="node_xy.md#D2-XY-Prompt-SR2">`D2 XY Prompt SR2`</a>
  - 搜索替換文字並以列表返回，放在 `D2 XY Plot` 後的類型
- <a href="node_xy.md#D2-XY-Seed">`D2 XY Seed`</a>
  - 輸出 SEED 列表
- <a href="node_xy.md#D2-XY-Seed2">`D2 XY Seed2`</a>
  - 輸出指定數量的SEED列表
- <a href="node_xy.md#D2-XY-Model-List">`D2 XY Model List`</a>
  - 輸出 Checkpoint / Lora 列表
- <a href="node_xy.md#D2-XY-Folder-Images">`D2 XY Folder Images`</a>
  - 輸出資料夾內文件列表
- <a href="node_xy.md#D2-XY-Upload-Image">`D2 XY Upload Image`</a>
  - 通過拖放上傳多個圖像
- <a href="node_xy.md#D2-XY-Annotation">`D2 XY Annotation`</a>
  - 創建在 `D2 Grid Image` 顯示的標題文字
- <a href="node_xy.md#D2-XY-List-To-Plot">`D2 XY List To Plot`</a>
  - 將陣列轉換為 `D2 XY Plot` 用列表
- <a href="node_xy.md#D2-XY-String-To-Plot">`D2 XY String To Plot`</a>
  - 將包含換行符的文本轉換為 `D2 XY Plot` 可用的列表格式


### 浮動面板

- <a href="node_float.md#D2-Queue-Button">`D2 Queue Button`</a>
  - 生成指定數量（Batch count）的按鈕
- <a href="node_float.md#Prompt-convert-dialog">`Prompt convert dialog`</a>
  - `NovelAI` 和 `StableDiffusion` 權重互相轉換的對話框
- <a href="node_float.md#D2-Progress-Preview">`D2 Progress Preview`</a>
  - 顯示生成中圖像的面板


## :blossom: 更新日誌

**2025.08.09**

- `D2_KSampler`: 新增對 Qwen-Image latent 的支援

**2025.08.07**

- `D2_SaveImageEagle` / `D2_SendFileEagle`: 新增功能

**2025.08.06**

- `D2_FilenameTemplate` / `D2_FilenameTemplate2`: 新增增減輸入項目功能。新增seed
- 更新了多個範例工作流程

**2025.08.05**

- `D2_SaveImage`: 新增對 WEBP、動畫WEBP 和 JPEG 格式的支援

**2025.07.19**

- `D2_CheckpointList` / `D2_LoraList`: 已刪除
- `D2_ImageResize`: 新增旋轉功能。也支援遮罩

**2025.06.22**

- `D2_SaveImage`: 新增功能

**2025.06.19**

- `D2_PromptConvert`: 支援NovelAI4的新權重方式

**2025.05.02**

- `D2_ProgressPreview`: 新增功能。
- `D2_XYUploadImage`: 新增加。

**2025.04.30**

- `D2_FolderImageQueue` `D2_FolderImages` `D2_LoadFolderImages`: 添加排序功能

**2025.04.28**

- `D2_FolderImageQueue`: 將起始編號從 `1` 更改為 `0`

**2025.04.24**

- `D2_FilenameTemplate2`：新增功能。支援多行的 `D2_FilenameTemplate` 版本
- `D2 EmptyImage Alpha` 顏色指定改為 red green blue。同時新增顏色樣本

**2025.04.22**

- `D2_CutByMask`: 新增了 `square_thumb` 模式，可使用最大尺寸的正方形進行裁剪
- `D2_XYFolderImages` / `D2_LoadFolderImages`: 修改為每次更新圖像列表。新增顯示圖像數量
- `D2_LoadImage`: 修復了在A1111中創建的PNG圖像提示無法輸出的錯誤

**2025.04.18**

- `D2_KSamplerAdvanced`: 添加了參數 `weight_interpretation` 和 `token_normalization` 用於調整提示詞權重
  - 使用需要安裝 [Advanced CLIP Text Encode](https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb/)。

**2025.04.16**

- `D2_Prompt`：添加LoRA插入按鈕
- `D2_KSampler` / `D2_KSamplerAdvanced`：支援A1111方式的LoRA載入提示詞。在KSampler內部進行LoRA載入
- `D2_LoadLora`：輸出的 `prompt` 更改為不刪除A1111方式的LoRA載入提示詞。傳統的輸出已重新命名為 `formatted_prompt`

**2025.04.14**

- `D2 Cut By Mask`: 新增功能
- `D2 Paste By Mask`: 新增功能
- `D2 XY Model List`: 支援升頻模型
- `D2 KSampler Advanced`: 輸出增加 d2_pipe

**2025.04.09**

- `D2_LoadImage`: 新增檔案名稱和檔案路徑的輸出
- `D2_FilenameTemplate`: 為`format`新增工具提示（滑鼠懸停時顯示）

**2025.04.06**

- `D2 Image Mask Stack`: 新增功能
- `D2 Mosaic Filter`: 新增功能

**2025.04.02**

- `D2 Prompt`：新增功能
- `D2 Delete Comment`：整合至`D2 Prompt`

**2025.03.31**

- `D2 Token Counter`: 新增功能

**2025.03.25**

- 新增註釋快捷鍵（ctrl + /）
- `D2 XYPlot Easy Mini`: 新增了 `D2 XYPlot Easy` 的輸出插槽受限版本

**2025.03.23**

- `D2 Delete Comment`: 新增功能
- `D2 Load Lora`: 新增使用A1111格式的選項
- `D2 Model List`: 新增以A1111格式獲取列表的選項

**2025.02.27**

- `D2 Load Lora`: 新增
- `D2 Multi Output`: 新增 x_list/ylist 輸出

**2025.02.23**

- `D2 Model and CLIP Merge SDXL`: 新增 checkpoint 合併節點

**2025.01.20**

- `D2 XY Seed2`: 新增節點
- `D2 XY Plot / D2 XY Plot Easy`: 新增可指定XY繪圖起始位置的功能
- `D2 XY Plot / D2 XY Plot Easy`: 新增XY繪圖預估剩餘時間顯示
- `D2 Regex Replace`: 新增可在替換字串中使用空白的功能

**2024.12.28**

- `D2 Pipe`: 新增節點
- `D2_KSampler / D2_XYPlotEasy`：將 xy_pipe 名稱更改為 d2_pipe

**2024.12.18**

- `D2 Filename Template`: 新增節點
- `D2 Grid Image`: 新增了可以通過圖片數量來指定網格圖像輸出觸發的功能

**2024.12.16**

- `D2 XY String To Plot`: 新增節點
- `D2 XY Grid Image`: 支援標籤中的換行符
- `D2 XY Grid Image`: 新增標籤輸出開關選項
- `D2 XY Prompt SR`: 支援包含換行符的文本
- `D2 XY Plot Easy`: 修改為在指定 seed 為 `-1` 時，在 `x/y_annotation` 中記錄隨機值

**2024.12.14**

- `D2 KSampler`：新增 `xy_pipe` 以連接 `D2 XY Plot Easy`
- `D2 Grid Image`：新增 `grid_pipe` 以連接 `D2 XY Plot` 和 `D2 XY Plot Easy`
- `D2 XY Plot Easy`：新增功能
- `D2 XY Model List`：新增檔案名稱和日期排序功能。新增支援 Sampler 和 Scheduler 列表獲取

**2024.12.05**

- 為 `D2 KSampler` / `D2 KSampler` 新增了 Conditioning 輸出
  
**2024.11.27**

- 新增 `D2 Preview Image`

**2024.11.23**

- 新增 `D2 Model List`

**2024.11.21**

- `D2 Checkpoint Loader`: 新增 Vpred（v_prediction）相關設定
- `D2 Image Resize`: 修改為可輸出 Latent


**2024.11.20**

- `D2 Image Resize`: 追加放大模型支援（如 SwinIR_4x）

**2024.11.18**

- 一次添加了許多功能
- 新增 `D2 Controlnet Loader`、`D2 Get Image Size`、`D2 Grid Image`、`D2 Image Stack`、`D2 List To String`、`D2 Load Folder Images`
- 新增 XY Plot 相關功能
- 新增 `D2 XY Annotation`、`D2 XY Checkpoint List`、`D2 XY Folder Images`、`D2 Grid Image`、`D2 XY List To Plot`、`D2 XY Lora List`、`D2 XY Plot`、`D2 XY Prompt SR`、`D2 XY Prompt SR2`、`D2 XY Seed`
- 現有節點也有修改，詳情請參考提交歷史記錄

**2024.11.02**

- `D2 Regex Switcher`: 新增輸入文字確認用文字區域的顯示/隱藏切換

**2024.10.28**

- 新增 `Prompt convert`: 用於 `NovelAI` 和 `StableDiffusion` 提示詞互相轉換的對話框
- `D2 Folder Image Queue`: 修復圖像生成數量不一致的問題

**2024.10.26**

- 新增 `D2 EmptyImage Alpha`
- 新增 `D2 Image Resize`
- 新增 `D2 Resize Calculator`


<details>
<summary><strong>2024.10.24</strong></summary>

- 新增 `D2 Regex Replace`
- 新增 `D2 Folder Image Queue`
- `D2 Load Image`: 新增圖像路徑輸入
- `D2 KSampler(Advanced)`: Input 新增 Positive / Negative Conditioning
</details>


<details>
  <summary><strong>2024.10.19</strong></summary>

- 新增 `D2 Queue Button`

</details>

<details>
  <summary><strong>2024.10.18</strong></summary>

- `D2 Size Selector`: 新增從圖像獲取尺寸的功能
- `D2 Size Selector`: 新增可選擇「四捨五入」和「捨去」的調整方式

</details>

<details>
<summary><strong>2024.10.14</strong></summary>

- `D2 Load Image`: 修復處理無 Exif 數據圖像（如從剪貼板貼上）時的錯誤

</details>

<details>
  <summary><strong>2024.10.11</strong></summary>

- `D2 Regex Switcher`: 新增在連接字串時可指定分隔符

</details>

<details>
  <summary><strong>2024.10.10</strong></summary>

- `D2 Load Image`: 新增 "Open Mask Editor" 按鈕

</details>

<details>
  <summary><strong>2024.10.08</strong></summary>
  
  - `D2 Load Image`: 新增功能

</details>

<details>
  <summary><strong>2024.10.03</strong></summary>

- `D2 Regex Switcher`: 修復匹配搜索但未處理的問題

</details>

<details>
  <summary><strong>2024.10.02</strong></summary>

- 整合現有節點創建

</details>
