# D2 KSampler / D2 KSampler(Advanced)

## 與標準KSampler的差異

- 直接輸出圖像（不需要VAE Decoder）
- 可以用STRING格式輸入提示詞
- 支援A1111方式的LoRA載入提示詞
    - 例如：`<lora:foo.safetensors:1>`
    - 格式請參考 <a href="https://github.com/da2el-ai/D2-nodes-ComfyUI/blob/main/docs/zh/node.md#D2-Load-Lora">`D2 Load Lora`</a>
    - 註：當在`D2 KSampler Advanced`中輸入`positive_cond` / `negative_cond`時，LoRA將不會套用到CLIP。只會套用到MODEL。
- 有專用的Controlnet輸入，可以簡單地應用
- 支援整合生成參數的 `d2_pipe`
    - 可以從 `D2 XY Plot`、`D2 XY Plot Easy`、`D2 XY Plot Easy Mini` 簡單接收
    - 可以簡單地將參數傳遞給 `D2 Send Eagle`
- 可以更改提示詞權重算法（weight_interpretation）

## 注意事項

- 當連接 `d2_pipe` 時，`d2_pipe` 的參數優先
- 例如，如果在 `D2 KSampler` 中指定 **steps:20**，在 `D2 XYPlot Easy` 中指定 **steps:15**，在連接 `d2_pipe` 的情況下，將採用 `D2 XYPlot Easy` 的 **steps:15**。

## Input

- 與標準KSampler相同
    - `model` / `clip` / `latent_image` / `seed` / `steps` / `cfg` / `sampler_name` / `scheduler` / `denoise`
- D2 KSampler中新增
    - `vae`
    - `cnet_stack`：用於連接 `D2 Controlnet Loader`
    - `d2_pipe`：整合的生成參數。從 `D2 XY Plot` 等節點接收
    - `preview_method`：生成時的預覽顯示方式
    - `positive` / `negative`：STRING格式的提示詞
- D2 KSampler Advanced中新增
    - `token_normalization` / `weight_interpretation`
        - 提示詞權重調整方法。可在 D2 KSampler Advanced 中使用
        - 使用需要安裝 [Advanced CLIP Text Encode](https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb/)

## Output

- 與標準KSampler相同
    - `LATENT`
- D2 KSampler中新增
    - `IMAGE`：生成的圖像
    - `MODEL` / `CLIP`：已套用LoRA
    - `positive` / `negative`：輸入的直接傳遞
    - `formatted_positive`：已刪除A1111方式LoRA格式的positive提示詞
    - `positive_cond` / `negative_cond`：已套用Controlnet的CONDITIONING
    - `d2_pipe`：整合的生成參數
