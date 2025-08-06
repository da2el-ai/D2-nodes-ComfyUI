<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



<h1>
Workflow
</h1>

画像を ComfyUI にドロップするとワークフローを再現できます。


## :card_index_dividers: シンプルな txt2img

<a href="../../workflow/simple_t2i_20250806.png"><img src="../../workflow/simple_t2i_20250806.png"></a>

- Lora も Controlnet も使わないシンプルな txt2img。


## :card_index_dividers: LoRA を使用した txt2img

<a href="../../workflow/lora_t2i_20250806.png"><img src="../../workflow/lora_t2i_20250806.png"></a>

- StableDiffusion webui A1111 と同じ書式で Lora を利用する txt2img。
- D2 Prompt を使うと Loraを呼び出しやすいです


## :card_index_dividers: txt2img + Hires fix

<a href="../../workflow/hiresfix_20250806.png"><img src="../../workflow/hiresfix_20250806.png"></a>

- D2 KSampler を2個、間に D2 Image Resize を入れて SwinR_4x を使用した Hires fix。



## :card_index_dividers: 生成パラメーターをファイル名に入れる

<a href="../../workflow/filename_template_20250806.png"><img src="../../workflow/filename_template_20250806.png"></a>

- D2 Filename Template を使ってファイル名を生成
- D2 Send File Eagle は別のカスタムノード <a href="https://github.com/da2el-ai/ComfyUI-d2-send-eagle" target="_blank">ComfyUI-d2-send-eagle</a>
 に収録されています


## :card_index_dividers: フォルダー内画像を一括でアップスケール

<a href="../../workflow/folder_image_queue_upscale_20250120.png"><img src="../../workflow/folder_image_queue_upscale_20250120.png"></a>

- フォルダー内画像を全て取得し、プロンプトを取得
- Controlnet anyTestを使用
- 1.5倍にアップスケールしている
- D2 XY Seed2 で出力枚数を指定


## :card_index_dividers: XY Plot: Checkpoint & Prompt S/R

<a href="../../workflow/xy_easy_20250121.png"><img src="../../workflow/xy_easy_20250121.png"></a>

- D2 XY Plot Easy を使ったシンプルな XY Plot

## :card_index_dividers: XY Plot: Lora

<a href="../../workflow/xy_easy_lora_20250806.png"><img src="../../workflow/xy_easy_lora_20250806.png"></a>

- Lora のテスト


## :card_index_dividers: Checkpoint Test 

<a href="../../workflow/checkpoint_test_20241218.png"><img src="../../workflow/checkpoint_test_20241218.png"></a>

- チェックポイントテスト用の画像を一括で生成
- 4種類のプロンプトを生成して1枚の画像に結合する
- XY Plot と違い、チェックポイントごとに別の画像を保存する



## :card_index_dividers: XY Plot: Prompt S/R

<a href="../../workflow/xy_prompt_sr_20250121.png"><img src="../../workflow/xy_prompt_sr_20250121.png"></a>

- Checkpointの系統（SDXL / Pony / Illustrious）によってクオリティタグを切り替えるXYプロット
- Animagine系、Pony系、Illustrious系はクオリティタグが異なるが、チェックポイントのパスを判断して自動的に切り替える
- ファイル名に系統の名前が入っているとは限らないので、系統名のフォルダに分類しておく必要がある


## :card_index_dividers: Refiner: Checkpoint を途中で切り替え Hires.fix

<a href="../../workflow/Refiner_20241218.png"><img src="../../workflow/Refiner_20241218.png"></a>


