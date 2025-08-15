<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



# Workflow

> [!TIP]
> **將圖像拖放到 ComfyUI 即可重現工作流程。**

## :card_index_dividers: 簡單的 txt2img

<a href="../../workflow/simple_t2i_20250806.png"><img src="../../workflow/simple_t2i_20250806.png"></a>

- 不使用 Lora 或 Controlnet 的簡單 txt2img。

## :card_index_dividers: 使用LoRA的txt2img

<a href="../../workflow/lora_t2i_20250806.png"><img src="../../workflow/lora_t2i_20250806.png"></a>

- 使用與StableDiffusion webui A1111相同格式的Lora的txt2img。
- 使用D2 Prompt可以更容易地使用Lora

## :card_index_dividers: txt2img + Hires fix

<a href="../../workflow/hiresfix_20250806.png"><img src="../../workflow/hiresfix_20250806.png"></a>

- 使用兩個 D2 KSampler，中間加入 D2 Image Resize，使用 SwinR_4x 的 Hires fix。

## :card_index_dividers: 在檔案名中包含生成參數

<a href="../../workflow/filename_template_20250808.png"><img src="../../workflow/filename_template_20250808.png"></a>

- 此範例使用 `D2 Save Image Eagle` 保存文件
- 使用 `D2 Filename Template` 生成檔案名
- 使用 `D2 Filename Template2` 生成Eagle備忘錄


## :card_index_dividers: 批量放大資料夾內的圖像

<a href="../../workflow/folder_image_queue_upscale_20250120.png"><img src="../../workflow/folder_image_queue_upscale_20250120.png"></a>

- 獲取資料夾內所有圖像和提示詞
- 使用 Controlnet anyTest
- 放大1.5倍
- 使用D2 XY Seed2指定輸出數量


## :card_index_dividers: XY Plot: Checkpoint 和 Prompt S/R

<a href="../../workflow/xy_easy_20250121.png"><img src="../../workflow/xy_easy_20250121.png"></a>

- 使用 D2 XY Plot Easy 的簡單 XY Plot

## :card_index_dividers: XY Plot: Lora Test

<a href="../../workflow/xy_easy_lora_20250815.png"><img src="../../workflow/xy_easy_lora_20250815.png"></a>

- Lora 的測試
- XY Plot的替換詞設定為日文的「なし」（無）。使用日文是因為它不會被識別為提示詞。當然，您可以使用任何您喜歡的詞
- Seed固定為 `11111` 和 `22222`
- `D2 KSampler` 的參數會被 `D2 XYPlot Easy` 覆蓋

## :card_index_dividers: Checkpoint Test

<a href="../../workflow/checkpoint_test_20241218.png"><img src="../../workflow/checkpoint_test_20241218.png"></a>

- 批量生成檢查點測試圖像
- 生成4種不同的提示詞並合併為一張圖像
- 與 XY Plot 不同，為每個檢查點保存單獨的圖像


## :card_index_dividers: XY Plot: Prompt S/R

<a href="../../workflow/xy_prompt_sr_20250121.png"><img src="../../workflow/xy_prompt_sr_20250121.png"></a>

- 根據Checkpoint類型（SDXL / Pony / Illustrious）切換品質標籤的XY繪圖
- Animagine系列、Pony系列和Illustrious系列具有不同的質量標籤，但根據檢查點路徑自動切換
- 由於文件名可能不包含系列名稱，需要將文件分類到相應系列的資料夾中



## :card_index_dividers: Refiner: 切換檢查點的 Hires.fix

<a href="../../workflow/Refiner_20241218.png"><img src="../../workflow/Refiner_20241218.png"></a>
