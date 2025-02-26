<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



# Node

## :tomato: Sampler Nodes

### D2 KSampler / D2 KSampler(Advanced)

<figure>
<img src="../img/ksampler_2.png">
</figure>

- KSampler that can input prompts as STRING

#### Input

- `cnet_stack`
  - For connecting to `D2 Controlnet Loader`
- `model` / `clip` / `vae` / ..etc
    - Same as standard KSampler
- `negative` / `positive`
    - Prompts in STRING format

#### Output

- `IMAGE`
    - Image output
- `positive` / `negative`
    - Input passthrough


---

### D2 Pipe

<figure>
<img src="../img/pipe.png">
</figure>

- A node for modifying and extracting the contents of `d2_pipe`
- `d2_pipe` is used to pass parameters collectively in nodes such as D2 XY Plot Easy, D2 KSampler, and D2 Send Eagle


---

## :tomato: Loader Node

### D2 Checkpoint Loader

<img src="../img/checkpoint_loader_2.png">

- A Checkpoint Loader that outputs the full path of model files
- Can automatically apply v_prediction settings when the filename contains "vpred"

#### Input

- `ckpt_name`
  - Checkpoint name
- `auto_vpred`
  - `true`: Automatically applies v_prediction settings if the filename contains "vpred"
- `sampling` / `zsnr`
  - Same settings as ModelSamplingDiscrete (details unknown)
- `multiplier`
  - Same settings as RescaleCFG (details unknown)

#### Output

- `model` / `clip` / `vae`
    - Same as the conventional CheckpointLoader.
- `ckpt_name` / `ckpt_hash` / `ckpt_fullpath`
    - Checkpoint name, hash, and full path.

---

### D2 Controlnet Loader

<figure>
<img src="../img/controlnet.png">
</figure>

- Controlnet Loader that creates simple workflows when connected to `D2 KSampler`

#### Input

- `cnet_stack`
  - For connecting to `D2 Controlnet Loader`

#### Output

- `cnet_stack`
  - For connecting to `D2 KSampler` or `D2 Controlnet Loader`


---


### D2 Load Lora

<figure>
<img src="../img/loadlora.png">
</figure>

- Lora loader that can specify Lora with text
- model_weight / clip_weight can also be specified

#### Format

**Example: lora:foo / model_weight:1 / clip_weight:1**
If model_weight is not specified, "1" is applied
```
foo
```
**Example: lora:foo / model_weight:0.5 / clip_weight:0.5**
If clip_weight is not specified, the same value as model_weight is applied
```
foo:1
```
**Example: lora:foo / model_weight:2 / clip_weight:1**
```
foo:2:1
```
**Example: Using 2 types of Lora (1)**
Separate with a line break
```
foo:0.5
bar
```
**Example: Using 2 types of Lora (2)**
When writing 2 types in one line, separate with ","
```
foo:0.5,bar
```

Notation (2) is useful when you want to verify Lora with D2 XYPlot Easy, etc.
Please refer to the <a href="workflow.md">sample workflow</a>.

**Example: Comment out**
Lines starting with "//" or "#" will be ignored.
```
//foo:0.5
#bar
```

---

## :tomato: Size Node

### D2 Get Image Size

<figure>
<img src="../img/get_image_size.png">
</figure>

- Both outputs and displays size

---

### D2 Size Selector

<figure>
<img src="../img/sizeselector_2.png">
</figure>

- Node for selecting image size from presets
- Can also get size from images
- Rounding method can be selected from `Ceil / Float / None`

#### Input

- `images`
    - Used when getting size from images
    - `preset` must be set to `custom`
- `preset`
    - Size presets
    - Must be set to `custom` when using `width` `height` below or image sizes
    - Edit `/custom_nodes/D2-nodes-ComfyUI/config/sizeselector_config.yaml` to modify presets
- `width` / `height`
    - Width/height dimensions
    - `preset` must be set to `custom`
- `swap_dimensions`
    - Swap width/height
- `upscale_factor`
    - Value passed to other resize nodes. Does nothing in this node
- `prescale_factor`
    - Output width/height after resizing by this factor
- `round_method`
    - `Round`: Round to nearest
    - `Floor`: Round down
    - `None`: No rounding
- `batch_size`
    - Batch size to set for empty_latent

#### Output

- `width / height`
    - Input `width`, `height` multiplied by `prescale_factor`
- `upscale_factor` / `prescale_factor`
    - Passthrough of input
- `batch_size`
    - Passthrough of input
- `empty_latent`
    - Outputs latent created with specified size and batch size

---

### D2 Image Resize

<figure>
<img src="../img/image_resize.png">
</figure>

- Simple image resizing
- Precision up to 3 decimal places
- Can select rounding, floor, or ceiling
- Capable of upscaling using upscale models
- Latent output is also possible (requires VAE)

---

### D2 Resize Calculator

<figure>
<img src="../img/resize_calc.png">
</figure>

- Can select rounding, floor, or ceiling

---



## :tomato: Refiner Node

### D2 Refiner Steps

<figure>
<img src="../img/refiner_steps.png">
</figure>

- Node for outputting steps for Refiner

#### Input

- `steps`
    - Total step count
- `start`
    - Starting steps for first KSampler
- `end`
    - Ending steps for first KSampler

#### Output

- `steps` / `start` / `end`
    - Input passthrough
- `refiner_start`
    - Starting steps for second KSampler

---

### D2 Refiner Steps A1111

<figure>
<img src="../img/refiner_a1111.png">
</figure>

- Node that can specify denoise for Refiner in img2img

#### Input

- `steps`
    - Total step count
- `denoise`
    - Specify denoise for img2img
- `switch_at`
    - What percentage of total steps to switch to next KSampler

#### Output

- `steps`
    - Input passthrough
- `start`
    - Starting steps for first KSampler
- `end`
    - Ending steps for first KSampler
- `refiner_start`
    - Starting steps for second KSampler

---

### D2 Refiner Steps Tester

- Node for checking steps


---


## :tomato: Merge Node


### D2 Model and CLIP Merge SDXL

<figure>
  <img src="../img/merge_sdxl.png">
</figure>

- A node that combines ModelMergeSDXL and CLIPMergeSimple
- Allows comma-separated weight specifications for easier use with XYPlot
- In this figure, `0.85,0.85,1,1,0.4,0.4,1,0.4,0.4,0.4,1,0.4,0.4,0.4,0,0.55,0.85,0.85,0.85,0.85,0.85,0.85,1,1,0.65` is specified


