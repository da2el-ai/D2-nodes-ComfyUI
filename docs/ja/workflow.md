<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a>
- <a href="workflow.md">Workflow</a>



<h1>
Workflow
</h1>

画像を ComfyUI にドロップするとワークフローを再現できます。


## :card_index_dividers: シンプルな txt2img

<a href="../../workflow/simple_t2i_20241218.png"><img src="../../workflow/simple_t2i_20241218.png"></a>

- Lora も Controlnet も使わないシンプルな txt2img。


## :card_index_dividers: txt2img + Hires fix

<a href="../../workflow/hiresfix_20241218.png"><img src="../../workflow/hiresfix_20241218.png"></a>

- D2 KSampler を2個、間に D2 Image Resize を入れて SwinR_4x を使用した Hires fix。



## :card_index_dividers: フォルダー内画像を一括でアップスケール

<a href="../../workflow/folder_image_queue_upscale_20250120.png"><img src="../../workflow/folder_image_queue_upscale_20250120.png"></a>

- フォルダー内画像を全て取得し、プロンプトを取得
- Controlnet anyTestを使用
- 1.5倍にアップスケールしている
- D2 XY Seed2 で出力枚数を指定


## :card_index_dividers: XY Plot: Checkpoint & Prompt S/R

<a href="../../workflow/xy_easy_20241214.png"><img src="../../workflow/xy_easy_20241214.png"></a>

- D2 XY Plot Easy を使ったシンプルな XY Plot


## :card_index_dividers: Checkpoint Test 

<a href="../../workflow/checkpoint_test_20241218.png"><img src="../../workflow/checkpoint_test_20241218.png"></a>

- チェックポイントテスト用の画像を一括で生成
- 4種類のプロンプトを生成して1枚の画像に結合する
- XY Plot と違い、チェックポイントごとに別の画像を保存する



## :card_index_dividers: XY Plot: Prompt S/R

<a href="../../workflow/xy_prompt_sr_20241218.png"><img src="../../workflow/xy_prompt_sr_20241218.png"></a>

- 基本的な Prompt S/R


## :card_index_dividers: XY Plot: Animagine、Pony、Illustrious の Chedckpoint 比較

<a href="../../workflow/xy_checkpint_20241119.png"><img src="../../workflow/xy_checkpint_20241119.png"></a>

- Animagine系、Pony系、Illustrious系はクオリティタグが異なるが、チェックポイントのパスを判断して自動的に切り替える
- ファイル名に系統の名前が入っているとは限らないので、系統名のフォルダに分類しておく必要がある


## :card_index_dividers: Refiner: Checkpoint を途中で切り替え Hires.fix

<a href="../../workflow/Refiner_20241218.png"><img src="../../workflow/Refiner_20241218.png"></a>


