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

<a href="../../workflow/simple_t2i_20241119.png"><img src="../../workflow/simple_t2i_20241119.png"></a>

- Lora も Controlnet も使わないシンプルな txt2img。


## :card_index_dividers: フォルダー内画像を一括でアップスケール

<a href="../../workflow/folder_image_queue_upscale_20241119.png"><img src="../../workflow/folder_image_queue_upscale_20241119.png"></a>

- フォルダー内画像を全て取得し、プロンプトを取得
- Controlnet anyTestを取得
- 1.5倍にアップスケールしている


## :card_index_dividers: XY Plot: Prompt S/R

<a href="../../workflow/xy_prompt_sr_20241119.png"><img src="../../workflow/xy_prompt_sr_20241119.png"></a>

- 基本的な Prompt S/R


## :card_index_dividers: XY Plot: Animagine、Pony、Illustrious の Chedckpoint 比較

<a href="../../workflow/xy_checkpint_20241119.png"><img src="../../workflow/xy_checkpint_20241119.png"></a>

- Animagine系、Pony系、Illustrious系はクオリティタグが異なるが、チェックポイントのパスを判断して自動的に切り替える
- ファイル名に系統の名前が入っているとは限らないので、系統名のフォルダに分類しておく必要がある


## :card_index_dividers: Refiner: Checkpoint を途中で切り替え Hires.fix

<a href="../../workflow/Refiner_20241119.png"><img src="../../workflow/Refiner_20241119.png"></a>


