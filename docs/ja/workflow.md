<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



<h1>
Workflow
</h1>

> [!TIP]
> **画像を ComfyUI にドロップするとワークフローを再現できます。**


## :card_index_dividers: シンプルな txt2img

<a href="../../workflow/simple_t2i_20260701.png"><img src="../../workflow/simple_t2i_20260701.png"></a>

> <a href="../../workflow/simple_t2i_20260701.json">ワークフローのダウンロード</a>

- Lora も Controlnet も使わないシンプルな txt2img。
- Model / CLIP / VAE は d2_pipe で渡している


---

## :card_index_dividers: LoRA を使用した txt2img

<a href="../../workflow/lora_t2i_20260701.png"><img src="../../workflow/lora_t2i_20260701.png"></a>

> <a href="../../workflow/lora_t2i_20260701.json">ワークフローのダウンロード</a>

- StableDiffusion webui A1111 と同じ書式で Lora を利用する txt2img。
- D2 Prompt の `CHEESE` ボタンからLoraを呼び出せます
- Model / CLIP / VAE は d2_pipe で渡している


---


## :card_index_dividers: txt2img + Hires fix

<a href="../../workflow/hiresfix_20260701.png"><img src="../../workflow/hiresfix_20260701.png"></a>

> <a href="../../workflow/hiresfix_20260701.json">ワークフローのダウンロード</a>

- D2 KSampler を2個置き、間に D2 Image Resize を入れて SwinR_4x を使用した Hires fix。
- Model / CLIP / VAE は d2_pipe で渡している


---

## :card_index_dividers: 生成パラメーターをファイル名に入れる

<a href="../../workflow/filename_template_20260701.png"><img src="../../workflow/filename_template_20260701.png"></a>

> <a href="../../workflow/filename_template_20260701.json">ワークフローのダウンロード</a>

- この例ではファイルの保存に `D2 Save Image Eagle` を使用
- `D2 Filename Template` を使ってファイル名を生成
- `d2_pipe` から入力された情報で Eagleメモを自動作成して保存


---

## :card_index_dividers: フォルダー内画像を一括でアップスケール

<a href="../../workflow/folder_image_queue_upscale_20260701.png"><img src="../../workflow/folder_image_queue_upscale_20260701.png"></a>

> <a href="../../workflow/folder_image_queue_upscale_20260701.json">ワークフローのダウンロード</a>


- `D2 Folder Image Queue` でフォルダー内画像を全て取得し、`D2 Load Image` でプロンプトとファイル名を取得
- アップスケールモデルに `4x-AnimeSharp` を使用（もちろん `None` でもよい）
- 1.5倍にアップスケールしている
- `D2 XY Seed2` で seed を4つ渡すことで4枚ずつ出力している
- Model / CLIP / VAE は d2_pipe で渡している


---

## :card_index_dividers: XY Plot: Checkpoint & Prompt S/R

<a href="../../workflow/xy_easy_20260701.png"><img src="../../workflow/xy_easy_20260701.png"></a>

> <a href="../../workflow/xy_easy_20260701.json">ワークフローのダウンロード</a>

- D2 XY Plot Easy Mini を使った XY Plot
- `D2 KSampler` のパラメーターは `D2 XYPlot Easy Mini` によって上書きされる
- グリッド画像は大きなサイズになるのでJPEG形式で保存している
- このサンプルでは画像保存に `D2 Save Image Eagle` を使用
- Diffusion Model の XY Plot の使い方は下記の記事を参照
  - https://note.com/da2el_ai/n/n4bc9002c61b1

---

## :card_index_dividers: Checkpoint Test 

<a href="../../workflow/checkpoint_test_20260701.png"><img src="../../workflow/checkpoint_test_20260701.png"></a>

> <a href="../../workflow/checkpoint_test_20260701.json">ワークフローのダウンロード</a>

- チェックポイントテスト用の画像を一括で生成
- 4種類のプロンプトを生成して1枚の画像に結合する
- プロンプトの数と、 `D2 Grid Image` の `trigger_count` の数を一致させている（サンプルでは`4`）
- 1個目の `D2 KSampler` は `D2 XY Plot Easy Mini` から受け取った生成パラメーターを使用するが、2個目の `D2 KSampler` は独自の設定を使用している
- `D2 Filename Template` を使ってチェックポイント名をファイル名に入れている


