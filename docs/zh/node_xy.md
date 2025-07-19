<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>




# Node


## :tomato: XY Plot Node


### D2 XY Plot Easy

<figure>
<img src="../img/xyplot_easy.png">
</figure>

- 一個可建立限定於 KSampler 項目的簡化工作流程 XY Plot 的節點

#### 輸入

- `positive` / `negative` / `seed` / `steps` / `cfg` / `sampler_name` / `scheduler` / `denoise`
  - 傳遞給 KSampler 的設定
- `ckpt_name`
  - 傳遞給 D2 Checkpoint Loader 的設定
- `x_type` / `y_type`
  - 指定要在 XY Plot 中執行的項目
  - 當指定為 `STRING`、`INT`、`FLOAT` 時，將從 `x_other`、`y_other` 輸出
- `x_list` / `y_list`
  - XY Plot 的變更內容
  - 因為是換行分隔的文字，所以也可以使用其他節點輸入
- `auto_queue`
  - `true`：自動執行所需次數的 Queue
  - `false`：手動執行 Queue
- `Reset index`
  - 中途停止時使用此按鈕重置索引

#### 輸出

- `xy_pipe`
  - 統一輸出用於 D2 KSampler 的參數
- `grid_pipe`
  - 統一輸出用於 D2 Grid Image 的參數 `x_annotation` `y_annotation` `status`
- `positive` / `negative` / `seed` / `steps` / `cfg` / `sampler_name` / `scheduler` / `denoise`
  - 傳遞給 KSampler 的參數
- `ckpt_name`
  - 傳遞給 D2 Checkpoint Loader 的設定
- `x_other` / `y_other`
  - 當 `x_type` `y_type` 設定為 `STRING` `INT` `FLOAT` 時從此處輸出
- `x_annotation` / `y_annotation`
  - 連接至 `D2 XY Grid Image` 的標題文字
- `status`
  - 連接至 `D2 XY Grid Image` 的控制信號
- `index`
  - 目前的處理次數

---


### D2 XY Plot

<figure>
<img src="../img/xyplot.png">
</figure>

- 可創建通用 XY Plot 工作流程的節點
- X / Y 輸入為簡單的換行分隔文字，易於與其他節點組合

#### Input

- `x_type` / `y_type`
  - 從 `STRING` `INT` `FLOAT` 中指定 `x_list` `y_list` 的數據類型
- `x_title` / `y_title`
  - 添加到標題文字的文字
- `x_list` / `y_list`
  - XY Plot 的變更內容
  - 為換行分隔文字，可使用其他節點輸入
- `auto_queue`
  - `true`: 自動執行所需次數的 Queue
  - `false`: 手動執行 Queue
- `Reset index`
  - 中途停止時用此按鈕重置 index

#### Output

- `X` / `Y`
  - 從 `x_list` `y_list` 獲取的元素
- `x_annotation` / `y_annotation`
  - 連接到 `D2 XY Grid Image` 的標題文字
- `status`
  - 連接到 `D2 XY Grid Image` 的控制信號
- `index`
  - 當前處理次數

---

### D2 XY Grid Image

<figure>
<img src="../img/xyplot.png">
</figure>

- 與 `D2 XY Plot` 連接使用的網格圖像創建節點

#### Input

- `x_annotation` / `y_annotation`
  - 連接到 `D2 XY Grid Image` 的標題文字
- `status`
  - 連接到 `D2 XY Grid Image` 的控制文字
  - `INIT`: 初始化
  - `FINISH`: 輸出網格圖像
  - `{空字串}`: 其他狀態
- `font_size`
  - 標題文字的字體大小
- `grid_gap`
  - 圖像間距
- `swap_dimensions`
  - `true`: 垂直方向網格
  - `false`: 水平方向網格
- `grid_only`
  - `true`: 僅輸出網格圖像
  - `false`: 也輸出個別圖像



---

### D2 XY Prompt SR

<figure>
<img src="../img/prompt_sr_2.png">
</figure>

- 搜索替換輸入文字並傳遞給 `D2 XY Plot`
- 也可輸出列表

#### Input

- `prompt`
    - 提示詞。可包含換行
- `search_txt`
    - 搜索目標文字。可包含多個詞
    - 不能使用換行
- `replace`
    - 替換用文字
    - 因為用換行分隔，所以可以包含「,」

#### Output

- `x / y_list`
  - 連接到 `D2 XY Plot`
- `LIST`
  - 以列表形式輸出替換後的文字

---

### D2 XY Prompt SR2

<figure>
<img src="../img/prompt_sr2.png?3">
</figure>

- 搜索替換從 `D2 XY Plot` 接收的提示詞並傳遞給 KSampler
- 如果要重現 `Stable Diffusion webui A1111` 的 Prompt S/R 請使用此節點

#### Input

- `x_y`
  - 從 `D2 XY Plot` 接收的替換用文字
- `prompt`
    - 替換目標文字
- `search`
    - 搜索文字。可包含多個詞
    - 不能使用換行

---

### D2 XY Seed

<figure>
<img src="../img/xy_seed.png?2">
</figure>

- 指定 `-1` 時輸出隨機數值
- 其他數值直接輸出
- `D2 XY Plot` 側需要將 `x/y_type` 設為 `INT`

---

### D2 XY Checkpoint List / D2 XY Lora List

已刪除。請使用 `D2 XY Model List` 代替。

---

### D2 XY Seed2

<figure>
  <img src="../img/xy_seed2.png?2">
</figure>

- 輸出指定數量種子值的節點

#### input
- `initial_number`
  - 當`mode`設為`increment`、`decrement`或`fixed`時，以此值為基準
- `count`
  - 要生成的種子值數量
- `mode`
  - `fixed`: 僅輸出`initial_number`
  - `increment`: 以`initial_number`為基礎，每次加1
  - `decrement`: 以`initial_number`為基礎，每次減1
  - `randomize`: 不考慮`initial_number`，輸出隨機數


---



### D2 XY Model List

<figure>
  <img src="../img/xy_model_list.png?2">
</figure>

- 將 Checkpoint/Lora 傳遞給 `D2 XY Plot` 的節點
- 當你想獲取大量模型列表，但不想在 `D2 Checkpoint List` 中一個一個選擇時使用
- 點擊 `get_list` 獲取模型列表，然後編輯保留需要的部分

#### input
- `model_type`
  - 選擇 `checkpoints` 或 `loras`
- `filter`
  - 輸入過濾文字
  - 支援正則表達式
  - 當搜尋文字包含 `\` 時，需寫成 `\\`
- `get_list`
  - 獲取模型列表按鈕


---


### D2 XY Upload Image

<figure>
  <img src="../img/xy_upload_image.png?2">
</figure>

- 一次性上傳多個圖像文件的節點
- 可以通過拖放文件將其上傳到臨時文件夾
- 上傳文件的路徑顯示在文本區域中
- 設計為通過 `D2 XY Plot Easy` 連接到 `D2 Load Image`


---


### D2 XY Folder Images

<figure>
<img src="../img/xy_folder_images.png">
</figure>

- 傳遞指定資料夾內圖像路徑到 `D2 XY Plot` 的節點

---

### D2 XY Annotation

<figure>
<img src="../img/xy_annotation.png?2">
</figure>

- 用於不使用 `D2 XY Plot` 時或進行特殊 XY Plot 時添加標題

---

### D2 XY List To Plot

<figure>
  <img src="../img/xy_list_to_plot.png?2">
</figure>

- 將列表輸出節點的內容轉換為可用於 `D2 XY Plot` 的格式
- 內部僅執行 `"\n".join(list)`，因此如果列表內容包含換行符，可能無法按預期工作
- 處理包含換行符的文本時，請使用 `D2 XY String To Plot`

---

### D2 XY String To Plot

<figure>
  <img src="../img/xy_string_to_plot.png">
</figure>

- 將多行文本轉換為可用於 `D2 XY Plot` / `D2 XY Plot Easy` 的格式
- 當需要比較整個提示詞時使用
- 在 `D2 XY Plot Easy` 中進行提示詞比較時，將 `x/y_type` 設置為 `STRING`，並將 `x/y_other` 連接到 `D2 KSampler` 的 `positive` 輸入
