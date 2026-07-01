<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



# Workflow

> [!TIP]
> **將圖像拖放到 ComfyUI 即可重現工作流程。**

## :card_index_dividers: 簡單的 txt2img

<a href="../../workflow/simple_t2i_20260701.png"><img src="../../workflow/simple_t2i_20260701.png"></a>

> <a href="../../workflow/simple_t2i_20260701.json">下載工作流程</a>

- 不使用 Lora 或 Controlnet 的簡單 txt2img。
- Model / CLIP / VAE 透過 d2_pipe 傳遞


---

## :card_index_dividers: 使用LoRA的txt2img

<a href="../../workflow/lora_t2i_20260701.png"><img src="../../workflow/lora_t2i_20260701.png"></a>

> <a href="../../workflow/lora_t2i_20260701.json">下載工作流程</a>

- 使用與StableDiffusion webui A1111相同格式的Lora的txt2img。
- 可以從 D2 Prompt 的 `CHEESE` 按鈕呼叫 Lora
- Model / CLIP / VAE 透過 d2_pipe 傳遞


---

## :card_index_dividers: txt2img + Hires fix

<a href="../../workflow/hiresfix_20260701.png"><img src="../../workflow/hiresfix_20260701.png"></a>

> <a href="../../workflow/hiresfix_20260701.json">下載工作流程</a>

- 放置兩個 D2 KSampler，中間加入 D2 Image Resize，使用 SwinR_4x 的 Hires fix。
- Model / CLIP / VAE 透過 d2_pipe 傳遞


---

## :card_index_dividers: 在檔案名中包含生成參數

<a href="../../workflow/filename_template_20260701.png"><img src="../../workflow/filename_template_20260701.png"></a>

> <a href="../../workflow/filename_template_20260701.json">下載工作流程</a>

- 此範例使用 `D2 Save Image Eagle` 保存文件
- 使用 `D2 Filename Template` 生成檔案名
- 使用 `d2_pipe` 輸入的信息自動創建 Eagle 備忘錄


---

## :card_index_dividers: 批量放大資料夾內的圖像

<a href="../../workflow/folder_image_queue_upscale_20260701.png"><img src="../../workflow/folder_image_queue_upscale_20260701.png"></a>

> <a href="../../workflow/folder_image_queue_upscale_20260701.json">下載工作流程</a>

- 使用 `D2 Folder Image Queue` 獲取資料夾內所有圖像，並使用 `D2 Load Image` 獲取提示詞與檔案名
- 使用 `4x-AnimeSharp` 放大模型（當然，也可以使用 `None`）
- 放大1.5倍
- 透過 `D2 XY Seed2` 傳遞4個 seed，每次輸出4張圖像
- Model / CLIP / VAE 透過 d2_pipe 傳遞


---

## :card_index_dividers: XY Plot: Checkpoint 和 Prompt S/R

<a href="../../workflow/xy_easy_20260701.png"><img src="../../workflow/xy_easy_20260701.png"></a>

> <a href="../../workflow/xy_easy_20260701.json">下載工作流程</a>

- 使用 D2 XY Plot Easy Mini 的 XY Plot
- `D2 KSampler` 的參數會被 `D2 XYPlot Easy Mini` 覆蓋
- 網格圖像較大，因此使用JPEG格式保存
- 此範例使用 `D2 Save Image Eagle` 保存圖像
- 關於如何在 Diffusion Model 上使用 XY Plot，請參考以下文章
  - https://note.com/da2el_ai/n/n4bc9002c61b1

---

## :card_index_dividers: Checkpoint Test

<a href="../../workflow/checkpoint_test_20260701.png"><img src="../../workflow/checkpoint_test_20260701.png"></a>

> <a href="../../workflow/checkpoint_test_20260701.json">下載工作流程</a>

- 批量生成檢查點測試圖像
- 生成4種不同的提示詞並合併為一張圖像
- 提示詞的數量與 `D2 Grid Image` 的 `trigger_count` 數量一致（範例中為 `4`）
- 第一個 `D2 KSampler` 使用從 `D2 XY Plot Easy Mini` 接收的生成參數，但第二個 `D2 KSampler` 使用自己的設置
- 使用 `D2 Filename Template` 將檢查點名稱加入檔案名
