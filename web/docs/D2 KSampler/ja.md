
# D2 KSampler / D2 KSampler(Advanced)

## 標準のKSamplerとの違い

- 画像を直接出力する（VAE Decoderが不要）
- プロンプトを文字列で入力できる
- A1111方式のLoRA読み込みプロンプトに対応
    - 例: `<lora:foo.safetensors:1>`
    - 書式は <a href="https://github.com/da2el-ai/D2-nodes-ComfyUI/blob/main/docs/ja/node.md#D2-Load-Lora">`D2 Load Lora`</a> を参照
    - `D2 KSampler Advanced` に `positive_cond` / `negative_cond` を入力した場合はCLIPにLoRAは適用されません。MODELのみ適用されます。
- Controlnet専用の入力があり、シンプルに適用できる
- 生成パラメーターをまとめた `d2_pipe` に対応
    - `D2 XY Plot` `D2 XY Plot Easy` `D2 XY Plot Easy Mini` から簡単に受け取れる
    - `D2 Send Eagle` へ簡単にパラメーターを渡せる
- プロンプトの重みアルゴリズムを変更できる（weight_interpretation）

## 注意点

- `d2_pipe` が接続されている場合は `d2_pipe` のパラメーターが優先されます
- 例えば `D2 KSampler` で **steps:20** を指定して、`D2 XYPlot Easy` で **steps:15** を指定。`d2_pipe` が接続されている状態だと　`D2 XYPlot Easy` の **steps:15** が採用されます。

## Input

- 標準のKSamplerと同じもの
    - `model` / `clip` / `latent_image` / `seed` / `steps` / `cfg` / `sampler_name` / `scheduler` / `denoise`
- D2 KSampler で追加したもの
    - `vae`
    - `cnet_stack`: `D2 Controlnet Loader` 接続用
    - `d2_pipe`: 生成パラメーターをまとめたもの。`D2 XY Plot` などから受け取る
    - `preview_method`: 生成時のプレビュー表示方式
    - `positive` / `negative`: 文字列形式のプロンプト入力
- D2 KSampler Advanced で追加したもの
    - `token_normalization` / `weight_interpretation`
        - プロンプトのウェイト調整方法。D2 KSampler Advancedで利用可能
        - 利用するには [Advanced CLIP Text Encode](https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb/) が必要


## Output

- 標準のKSamplerと同じもの
    - `LATENT`
- D2 KSampler で追加したもの
    - `IMAGE`: 生成画像
    - `MODEL` / `CLIP`: LoRA適用済み
    - `positive` / `negative`: Inputのものをそのまま出力
    - `formatted_positive`: A1111方式のLoRA書式を削除したpositiveプロンプト
    - `positive_cond` / `negative_cond`: Controlnet適用済みのCONDITIONING
    - `d2_pipe`: 生成パラメーターをまとめたもの
