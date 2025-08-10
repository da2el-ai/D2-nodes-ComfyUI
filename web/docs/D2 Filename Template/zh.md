# D2 Filename Template / D2 Filename Template2

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/filename_template_3.png">
</figure>

- 用於創建字符串模板的節點，可以整合日期和其他節點的參數
- `D2 Filename Template2` 是支持多行的版本

## 輸入

- `arg_{數字}`
  - 從其他節點導入值
- `format`
    - `%date:{yyyy/MM/dd/hh/mm/ss}%`
      - `yyyy`: 年
      - `MM`: 月
      - `dd`: 日
      - `hh`: 時
      - `mm`: 分
      - `ss`: 秒
    - `%{節點名稱}.{key}%`
      - 通過指定節點名稱和參數名稱獲取值
      - 例如：`%Empty Latent Image.width%`: 從 Empty Latent Image 節點獲取寬度
    - `%node:{id}.{key}%`
      - 通過指定節點 ID 和參數名稱獲取值
      - 例如：`%node:8.width%`: 從 ID 為 8 的節點獲取寬度
    - `%arg_{數字}%`
      - 嵌入輸入值
    - `%arg_{數字}:ckpt_name%`
      - 嵌入去除 `.safetensors` 的檢查點名稱
- `arg_count`
  - 增加或減少輸入項目的數量


## StableDiffusion A1111 webui PNGInfo 格式

<figure>
<img src="../img/save_image_eagle_3.png?2">
</figure>

在上面的示例中，`D2 KSampler` 的 `positive` 和 `negative` 被輸入到 `arg_1` 和 `arg_2` 並通過 `%arg_1%` 和 `%arg_2%` 獲取。其他參數通過 `%{節點名稱}.{Param}` 獲取。

```
%arg_1%

Negative prompt: %arg_2%
Steps: %D2 KSampler.steps%, Sampler: %D2 KSampler.sampler_name% %D2 KSampler.scheduler%, CFG scale: %D2 KSampler.cfg%, Seed: %D2 KSampler.seed%, Size: %Empty Latent Image.width%x%Empty Latent Image.height%, Model: %D2 Checkpoint Loader.ckpt_name%
```
輸出結果
```
masterpiece, 1girl, bikini, blue sky,

Negative prompt: bad quality, worst quality, sepia,
Steps: 20, Sampler: euler_ancestral simple, CFG scale: 5.000000000000001, Seed: 926243299419009, Size: 768x1024, Model: _SDXL_Illustrious\anime\HiyokoDarkness_vpred_v2_20250329.safetensors
```
