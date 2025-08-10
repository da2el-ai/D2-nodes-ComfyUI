
# D2 Filename Template / D2 Filename Template2

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/filename_template_3.png">
</figure>

- 日付や他のノードのパラメーターを取り込んで文字列テンプレートを作るためのノード
- `D2 Filename Template2` は複数行対応版です

## Input

- `arg_{数字}`
  - 他のノードから値を取り込む
- `format`
    - `%date:{yyyy/MM/dd/hh/mm/ss}%`
      - `yyyy`: 年
      - `MM`: 月
      - `dd`: 日
      - `hh`: 時
      - `mm`: 分
      - `ss`: 秒
    - `%{ノード名}.{key}%`
      - ノード名と、項目名を指定して値を取得する
      - 例：`%Empty Latent Image.width%`: Empty Latent Image のノードから width を取得
    - `%node:{id}.{key}%`
      - ノードIDと、項目名を指定して値を取得する
      - 例：`%node:8.width%`: ID 8 のノードから width を取得
    - `%arg_{数字}%`
      - 入力した値を埋め込む
    - `%arg_{数字}:ckpt_name%`
      - チェックポイント名から `.safetensors` を除外したものを埋め込む
- `arg_count`
  - 入力項目の増減


## StableDiffusion A1111 webui の PNGInfo書式

<figure>
<img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/save_image_eagle_3.png">
</figure>

上のサンプルでは `D2 KSampler` から `positive` `negative` を `arg_1` `arg_2` に入力して `%arg_1%` `%arg_2%` で取得、その他のパラメーターは `%{ノード名}.{Param}` で取得しています。

```
%arg_1%

Negative prompt: %arg_2%
Steps: %D2 KSampler.steps%, Sampler: %D2 KSampler.sampler_name% %D2 KSampler.scheduler%, CFG scale: %D2 KSampler.cfg%, Seed: %D2 KSampler.seed%, Size: %Empty Latent Image.width%x%Empty Latent Image.height%, Model: %D2 Checkpoint Loader.ckpt_name%
```
出力結果
```
masterpiece, 1girl, bikini, blue sky,

Negative prompt: bad quality, worst quality, sepia,
Steps: 20, Sampler: euler_ancestral simple, CFG scale: 5.000000000000001, Seed: 926243299419009, Size: 768x1024, Model: _SDXL_Illustrious\anime\HiyokoDarkness_vpred_v2_20250329.safetensors
```
