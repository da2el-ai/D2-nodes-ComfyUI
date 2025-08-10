# D2 Filename Template / D2 Filename Template2

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/filename_template_3.png">
</figure>

- Nodes for creating string templates by incorporating dates and parameters from other nodes
- `D2 Filename Template2` is a version that supports multiple lines

## Input

- `arg_{number}`
  - Import values from other nodes
- `format`
    - `%date:{yyyy/MM/dd/hh/mm/ss}%`
      - `yyyy`: Year
      - `MM`: Month
      - `dd`: Day
      - `hh`: Hour
      - `mm`: Minute
      - `ss`: Second
    - `%{node_name}.{key}%`
      - Get a value by specifying the node name and parameter name
      - Example: `%Empty Latent Image.width%`: Get width from the Empty Latent Image node
    - `%node:{id}.{key}%`
      - Get a value by specifying the node ID and parameter name
      - Example: `%node:8.width%`: Get width from the node with ID 8
    - `%arg_{number}%`
      - Embed the input value
    - `%arg_{number}:ckpt_name%`
      - Embed the checkpoint name with `.safetensors` removed
- `arg_count`
  - Increase or decrease the number of input items


## StableDiffusion A1111 webui PNGInfo Format

<figure>
<img src="../img/save_image_eagle_3.png?2">
</figure>

In the sample above, `positive` and `negative` from `D2 KSampler` are input to `arg_1` and `arg_2` and retrieved with `%arg_1%` and `%arg_2%`. Other parameters are retrieved with `%{node_name}.{Param}`.

```
%arg_1%

Negative prompt: %arg_2%
Steps: %D2 KSampler.steps%, Sampler: %D2 KSampler.sampler_name% %D2 KSampler.scheduler%, CFG scale: %D2 KSampler.cfg%, Seed: %D2 KSampler.seed%, Size: %Empty Latent Image.width%x%Empty Latent Image.height%, Model: %D2 Checkpoint Loader.ckpt_name%
```
Output result
```
masterpiece, 1girl, bikini, blue sky,

Negative prompt: bad quality, worst quality, sepia,
Steps: 20, Sampler: euler_ancestral simple, CFG scale: 5.000000000000001, Seed: 926243299419009, Size: 768x1024, Model: _SDXL_Illustrious\anime\HiyokoDarkness_vpred_v2_20250329.safetensors
```
