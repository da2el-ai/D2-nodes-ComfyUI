<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a>
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

### 文字

- <a href="node.md#D2-Regex-Replace">`D2 Regex Replace`</a>
  - 可設定多個條件的文字替換節點
- <a href="node.md#D2-Regex-Switcher">`D2 Regex Switcher`</a>
  - 根據輸入文字切換輸出文字的節點
  - 可進行字串連接
- <a href="node.md#D2-Multi-Output">`D2 Multi Output`</a>
  - 以列表形式輸出 SEED / STRING / INT / FLOAT
- <a href="node.md#D2-List-To-String">`D2 List To String`</a>
  - 將陣列轉換為字串

### 載入器

- <a href="node.md#D2-Checkpoint-Loader">`D2 Checkpoint Loader`</a>
  - 輸出模型文件完整路徑的 Checkpoint Loader
- <a href="node.md#D2-Controlnet-Loader">`D2 Controlnet Loader`</a>
  - 連接到 `D2 KSampler` 可建立簡單工作流程的 Controlnet Loader

### 圖像

- <a href="node.md#D2-Load-Image">`D2 Load Image`</a>
  - 可從圖像獲取提示詞的 Load Image
  - 支援 `StableDiffusion webui A1111`、`NovelAI` 創建的圖像
  - 附帶打開遮罩編輯器按鈕
- <a href="node.md#D2-Load-Folder-Images">`D2 Load Folder Images`</a>
  - 載入資料夾內的所有圖像
- <a href="node.md#D2-Folder-Image-Queue">`D2 Folder Image Queue`</a>
  - 依序輸出資料夾內的圖像路徑
  - 自動執行與圖像數量相應的佇列
- <a href="node.md#D2-Grid-Image">`D2 Grid Image`</a>
  - 生成網格圖像
- <a href="node.md#D2-Image-Stack">`D2 Image Stack`</a>
  - 用於堆疊多個圖像並傳遞給 `D2 Grid Image` 的節點
  - 直接輸出圖像
- <a href="node.md#D2-EmptyImage-Alpha">`D2 EmptyImage Alpha`</a>
  - 輸出帶有 α 通道（透明度）的 EmptyImage

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

### XY Plot

- <a href="node.md#D2-XY-Plot">`D2 XY Plot`</a>
  - 通用的 XY Plot 節點
  - 自動執行所需次數的佇列
- <a href="node.md#D2-XY-Grid-Image">`D2 XY Grid Image`</a>
  - 生成網格圖像的節點
- <a href="node.md#D2-XY-Prompt-SR">`D2 XY Prompt SR`</a>
  - 搜索替換文字並以列表返回，放在 `D2 XY Plot` 前的類型
- <a href="node.md#D2-XY-Prompt-SR2">`D2 XY Prompt SR2`</a>
  - 搜索替換文字並以列表返回，放在 `D2 XY Plot` 後的類型
- <a href="node.md#D2-XY-Seed">`D2 XY Seed`</a>
  - 輸出 SEED 列表
- <a href="node.md#D2-XY-Checkpoint-List">`D2 XY Checkpoint List`</a>
  - 輸出 Checkpoint 列表
- <a href="node.md#D2-XY-Lora-List">`D2 XY Lora List`</a>
  - 輸出 Lora 列表
- <a href="node.md#D2-XY-Folder-Images">`D2 XY Folder Images`</a>
  - 輸出資料夾內文件列表
- <a href="node.md#D2-XY-Annotation">`D2 XY Annotation`</a>
  - 創建在 `D2 Grid Image` 顯示的標題文字
- <a href="node.md#D2-XY-List-To-Plot">`D2 XY List To Plot`</a>
  - 將陣列轉換為 `D2 XY Plot` 用列表

### Refiner
- <a href="node.md#D2-Refiner-Steps">`D2 Refiner Steps`</a>
  - 輸出用於 Refiner 的步數
- <a href="node.md#D2-Refiner-Steps-A1111">`D2 Refiner Steps A1111`</a>
  - 用於 img2img 的 Refiner，可指定 denoise
- <a href="node.md#D2-Refiner-Steps-Tester">`D2 Refiner Steps Tester`</a>
  - 用於確認步數的節點

### 浮動面板

- <a href="node.md#D2-Queue-Button">`D2 Queue Button`</a>
  - 生成指定數量（Batch count）的按鈕
- <a href="node.md#Prompt-convert-dialog">`Prompt convert dialog`</a>
  - `NovelAI` 和 `StableDiffusion` 權重互相轉換的對話框


## :blossom: 更新日誌

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

