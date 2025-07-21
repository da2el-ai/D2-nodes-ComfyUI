# D2 KSampler / D2 KSampler(Advanced)

## Differences from standard KSampler

- Directly outputs images (VAE Decoder not required)
- Can input prompts in STRING format
- Supports A1111-style LoRA loading prompts
    - Example: `<lora:foo.safetensors:1>`
    - For format, refer to <a href="https://github.com/da2el-ai/D2-nodes-ComfyUI/blob/main/docs/en/node.md#D2-Load-Lora">`D2 Load Lora`</a>
    - Note: When inputting `positive_cond` / `negative_cond` to `D2 KSampler Advanced`, LoRA will not be applied to CLIP. It will only be applied to MODEL.
- Has dedicated Controlnet input for simple application
- Supports `d2_pipe` which consolidates generation parameters
    - Can easily receive from `D2 XY Plot`, `D2 XY Plot Easy`, `D2 XY Plot Easy Mini`
    - Can easily pass parameters to `D2 Send Eagle`
- Can change prompt weight algorithm (weight_interpretation)

## Notes

- When `d2_pipe` is connected, `d2_pipe` parameters take priority
- For example, if you specify **steps:20** in `D2 KSampler` and **steps:15** in `D2 XYPlot Easy`, with `d2_pipe` connected, **steps:15** from `D2 XYPlot Easy` will be used.

## Input

- Same as standard KSampler
    - `model` / `clip` / `latent_image` / `seed` / `steps` / `cfg` / `sampler_name` / `scheduler` / `denoise`
- Added in D2 KSampler
    - `vae`
    - `cnet_stack`: For connecting to `D2 Controlnet Loader`
    - `d2_pipe`: Consolidated generation parameters. Received from nodes like `D2 XY Plot`
    - `preview_method`: Preview display method during generation
    - `positive` / `negative`: Prompts in STRING format
- Added in D2 KSampler Advanced
    - `token_normalization` / `weight_interpretation`
        - Methods for adjusting prompt weights. Available in D2 KSampler Advanced
        - Requires [Advanced CLIP Text Encode](https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb/) to use

## Output

- Same as standard KSampler
    - `LATENT`
- Added in D2 KSampler
    - `IMAGE`: Generated image
    - `MODEL` / `CLIP`: With LoRA applied
    - `positive` / `negative`: Input passthrough
    - `formatted_positive`: Positive prompt with A1111-style LoRA format removed
    - `positive_cond` / `negative_cond`: CONDITIONING with Controlnet applied
    - `d2_pipe`: Consolidated generation parameters

