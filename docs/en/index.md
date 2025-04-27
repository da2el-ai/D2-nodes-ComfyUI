<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



# D2 Nodes ComfyUI

**D2 Nodes ComfyUI** is a collection of custom nodes created with the themes of "slightly convenient," "simple," and "maintaining versatility."

- Versatile XY Plot
- Workflow that automatically switches quality tags based on Checkpoint lineage
- Queue button with customizable batch count
- Various other "slightly convenient nodes"

## :exclamation: NOTICE

### Unnecessary Custom Nodes
If you have installed any of the following custom nodes previously, please remove them:

- [ComfyUI-d2-size-selector](https://github.com/da2el-ai/ComfyUI-d2-size-selector)
- [ComfyUI-d2-steps](https://github.com/da2el-ai/ComfyUI-d2-steps)
- [ComfyUI-d2-xyplot-utils](https://github.com/da2el-ai/ComfyUI-d2-xyplot-utils)

## :tomato: Nodes

- <a href="node.md#d2-ksampler--d2-ksampleradvanced">`D2 KSampler / D2 KSampler(Advanced)`</a>
  - KSampler that inputs and outputs prompts as STRING
- <a href="node.md#d2-pipe">`D2 Pipe`</a>
  - A node for modifying and retrieving the d2_pipe used in D2 XYPlot Easy, D2 KSampler, and D2 Send Eagle

### Loader

- <a href="node.md#D2-Checkpoint-Loader">`D2 Checkpoint Loader`</a>
  - Checkpoint Loader that outputs full model file paths
- <a href="node.md#D2-Controlnet-Loader">`D2 Controlnet Loader`</a>
  - Controlnet Loader that creates simple workflows when connected to D2 KSampler
- <a href="node.md#D2-Load-Lora">`D2 Load Lora`</a>
  - Lora loader that can be specified with text

### Size

- <a href="node.md#D2-Get-Image-Size">`D2 Get Image Size`</a>
  - Displays and retrieves image sizes
- <a href="node.md#D2-Size-Slector">`D2 Size Slector`</a>
  - Image size and Empty latent output node with preset selection
  - Can also get size from images
- <a href="node.md#D2-Image-Resize">`D2 Image Resize`</a>
  - Image resize with precision up to 3 decimal places
  - Options for rounding, floor, or ceiling
- <a href="node.md#D2-Resize-Calculator">`D2 Resize Calculator`</a>
  - Image size calculator that ensures results are multiples of 8
  - Options for rounding, floor, or ceiling


### Refiner
- <a href="node.md#D2-Refiner-Steps">`D2 Refiner Steps`</a>
  - Outputs steps for Refiner
- <a href="node.md#D2-Refiner-Steps-A1111">`D2 Refiner Steps A1111`</a>
  - Can specify denoise for Refiner in img2img
- <a href="node.md#D2-Refiner-Steps-Tester">`D2 Refiner Steps Tester`</a>
  - Node for checking steps

### Merge Node

- <a href="node.md#D2-Model-and-CLIP-Merge-SDXL">`D2 Model and CLIP Merge SDXL`</a>
  - A node that combines ModelMergeSDXL and CLIPMergeSimple

### Text

- <a href="node_text.md#D2-Regex-Replace">`D2 Regex Replace`</a>
  - Text replacement node with multiple condition support
- <a href="node_text.md#D2-Regex-Switcher">`D2 Regex Switcher`</a>
  - Node that switches output text based on input text
  - Can also perform string concatenation
- <a href="node_text.md#D2-Multi-Output">`D2 Multi Output`</a>
  - Outputs SEED / STRING / INT / FLOAT as lists
- <a href="node_text.md#D2-List-To-String">`D2 List To String`</a>
  - Converts arrays to strings
- <a href="node_text.md#D2-Filename-Template">`D2 Filename Template`</a>
  - Creates filenames
- <a href="node_text.md#D2-Token-Counter">`D2 Token Counter`</a>
  - Counts tokens in prompts
- <a href="node_text.md#D2-Prompt">`D2 Prompt`</a>
  - Text node with comment deletion function and token count display



### Image

- <a href="node_image.md#D2-Load-Image">`D2 Load Image`</a>
  - Load Image that can extract prompts from images
  - Compatible with images created in StableDiffusion webui A1111 and NovelAI
  - Includes a button to open mask editor
- <a href="node_image.md#D2-Load-Folder-Images">`D2 Load Folder Images`</a>
  - Loads all images from a folder
- <a href="node_image.md#D2-Folder-Image-Queue">`D2 Folder Image Queue`</a>
  - Sequentially outputs image paths from a folder
  - Automatically executes queue for all images
- <a href="node_image.md#D2-Grid-Image">`D2 Grid Image`</a>
  - Generates grid images
- <a href="node_image.md#D2-Image-Stack">`D2 Image Stack`</a>
  - Combines multiple images into a batch
- <a href="node_image.md#D2-Image-Mask-Stack">`D2 Image Mask Stack`</a>
  - Combines multiple images and masks into a batch
- <a href="node_image.md#D2-EmptyImage-Alpha">`D2 EmptyImage Alpha`</a>
  - Outputs EmptyImage with alpha channel (transparency)
- <a href="node_image.md#D2-Mosaic-Filter">`D2 Mosaic Filter`</a>
  - Applies a mosaic filter to images
- <a href="node_image.md#D2-Cut-By-Mask">`D2 Cut By Mask`</a>
  - Cut an image using a mask
- <a href="node_image.md#D2-Paste-By-Mask">`D2 Paste By Mask`</a>
  - Paste an image using a mask


### XY Plot

- <a href="node_xy.md#D2-XY-Plot-Easy">`D2 XY Plot Easy`</a>
  - A simplified XY Plot node limited to D2 KSampler parameters, designed for streamlined workflow
- <a href="node_xy.md#D2-XY-Plot">`D2 XY Plot`</a>
  - Versatile XY Plot node
  - Automatically executes required number of queues
- <a href="node_xy.md#D2-XY-Grid-Image">`D2 XY Grid Image`</a>
  - Node for generating grid images
- <a href="node_xy.md#D2-XY-Prompt-SR">`D2 XY Prompt SR`</a>
  - Searches and replaces text, returns as list. Placed before D2 XY Plot
- <a href="node_xy.md#D2-XY-Prompt-SR2">`D2 XY Prompt SR2`</a>
  - Searches and replaces text, returns as list. Placed after D2 XY Plot
- <a href="node_xy.md#D2-XY-Seed">`D2 XY Seed`</a>
  - Outputs list of SEEDs
- <a href="node_xy.md#D2-XY-Seed2">`D2 XY Seed2`</a>
  - Outputs a list of SEEDs with specified count
- <a href="node_xy.md#D2-XY-Checkpoint-List">`D2 XY Checkpoint List`</a>
  - Outputs list of Checkpoints
- <a href="node_xy.md#D2-XY-Lora-List">`D2 XY Lora List`</a>
  - Outputs list of Loras
- <a href="node_xy.md#D2-XY-Model-List">`D2 XY Model List`</a>
  - Outputs a list of Checkpoints / Loras
- <a href="node_xy.md#D2-XY-Folder-Images">`D2 XY Folder Images`</a>
  - Outputs list of files in folder
- <a href="node_xy.md#D2-XY-Annotation">`D2 XY Annotation`</a>
  - Creates header text for display in D2 Grid Image
- <a href="node_xy.md#D2-XY-List-To-Plot">`D2 XY List To Plot`</a>
  - Converts arrays to D2 XY Plot lists
- <a href="node_xy.md#D2-XY-String-To-Plot">`D2 XY String To Plot`</a>
  - Converts text containing line breaks into a list format for `D2 XY Plot`


### Float Palet

- <a href="node_float.md#D2-Queue-Button">`D2 Queue Button`</a>
  - Button that generates specified number of images (Batch count)
- <a href="node_float.md#Prompt-convert-dialog">`Prompt convert dialog`</a>
  - Dialog for converting weights between NovelAI and StableDiffusion




## :blossom: Changelog

**2025.04.28**

- `D2_FolderImageQueue`: Changed start number from `1` to `0`

**2025.04.24**

- `D2_FilenameTemplate2`: Newly added. Multiple line support version of `D2_FilenameTemplate`
- `D2 EmptyImage Alpha` color specification changed to red green blue. Color samples also added

**2025.04.22**

- `D2_CutByMask`: Added `square_thumb` mode to cut with maximum-sized square
- `D2_XYFolderImages` / `D2_LoadFolderImages`: Changed to update the image list every time. Added display of image count
- `D2_LoadImage`: Fixed a bug where prompts from PNG images created in A1111 were not being output

**2025.04.18**

- `D2_KSamplerAdvanced`: Added parameters `weight_interpretation` and `token_normalization` to adjust prompt weights
  - Requires [Advanced CLIP Text Encode](https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb/) to use.

**2025.04.16**

- `D2_Prompt`: Add LoRA insertion button
- `D2_KSampler` / `D2_KSamplerAdvanced`: Support A1111-style LoRA loading prompts. Load LoRA inside KSampler
- `D2_LoadLora`: Changed the output `prompt` to output A1111-style LoRA loading prompts without removing them. The conventional output has been renamed to `formatted_prompt`

**2025.04.14**

- `D2 Cut By Mask`: Newly added
- `D2 Paste By Mask`: Newly added
- `D2 XY Model List`: Added support for upscaler models
- `D2 KSampler Advanced`: Added d2_pipe to outputs

**2025.04.09**

- `D2_LoadImage`: Added output of filename and file path
- `D2_FilenameTemplate`: Added tooltip to `format` (displayed on mouse hover)

**2025.04.06**

- `D2 Image Mask Stack`: Newly added
- `D2 Mosaic Filter`: Newly added

**2025.04.02**

- `D2 Prompt`: Newly added
- `D2 Delete Comment`: Integrated into `D2 Prompt`

**2025.03.31**

- `D2 Token Counter`: Newly added

**2025.03.25**

- Added comment shortcut key (ctrl + /)
- `D2 XYPlot Easy Mini`: Added a version of `D2 XYPlot Easy` with limited output slots

**2025.03.23**

- `D2 Delete Comment`: Newly added
- `D2 Load Lora`: Added option to enable the use of A1111 format
- `D2 Model List`: Added option to retrieve in A1111 format


**2025.02.27**

- `D2 Load Lora`: Newly added
- `D2 Multi Output`: Added x_list/ylist output

**2025.02.23**

- `D2 Model and CLIP Merge SDXL`: Added checkpoint merge nodes

**2025.01.20**

- `D2 XY Seed2`: Added new node
- `D2 XY Plot / D2 XY Plot Easy`: Added ability to specify XY plot starting position
- `D2 XY Plot / D2 XY Plot Easy`: Added estimated time remaining display for XY plots
- `D2 Regex Replace`: Added support for using whitespace in replacement strings

**2024.12.28**

- `D2 Pipe`: Added new node
- `D2_KSampler / D2_XYPlotEasy`: Changed xy_pipe name to d2_pipe

**2024.12.18**

- `D2 Filename Template`: Added new node
- `D2 Grid Image`: Added the ability to specify the grid image output trigger by the number of images

**2024.12.16**

- `D2 XY String To Plot`: Added new node
- `D2 XY Grid Image`: Added support for line breaks in labels
- `D2 XY Grid Image`: Added option to toggle label output
- `D2 XY Prompt SR`: Added support for text containing line breaks
- `D2 XY Plot Easy`: Modified to record random values in `x/y_annotation` when `-1` is specified for seed

**2024.12.14**

- `D2 KSampler`: Added `xy_pipe` for connection with `D2 XY Plot Easy`
- `D2 Grid Image`: Added `grid_pipe` for connection with `D2 XY Plot` and `D2 XY Plot Easy`
- `D2 XY Plot Easy`: Newly added
- `D2 XY Model List`: Added filename and date sorting. Added support for retrieving Sampler and Scheduler lists

**2024.12.05**

- Added Conditioning output to `D2 KSampler` / `D2 KSampler`

**2024.11.27**

- Added new `D2 Preview Image`

**2024.11.23**

- Added new `D2 Model List`

**2024.11.21**

- `D2 Checkpoint Loader`: Added settings for Vpred (v_prediction)
- `D2 Image Resize`: Modified to enable Latent output

**2024.11.20**

- `D2 Image Resize`: Added support for upscale models (like SwinIR_4x)

**2024.11.18**

- Added many nodes at once
- Added `D2 Controlnet Loader`, `D2 Get Image Size`, `D2 Grid Image`, `D2 Image Stack`, `D2 List To String`, `D2 Load Folder Images`
- Added XY Plot related nodes
- Added `D2 XY Annotation`, `D2 XY Checkpoint List`, `D2 XY Folder Images`, `D2 Grid Image`, `D2 XY List To Plot`, `D2 XY Lora List`, `D2 XY Plot`, `D2 XY Prompt SR`, `D2 XY Prompt SR2`, `D2 XY Seed`
- Existing nodes have also been modified, see commit history for details

**2024.11.02**

- `D2 Regex Switcher`: Added toggle for input text confirmation textarea

**2024.10.28**

- Added `Prompt convert`: Dialog for converting prompts between NovelAI and StableDiffusion
- `D2 Folder Image Queue`: Fixed issue where image generation count was inconsistent

**2024.10.26**

- Added new `D2 EmptyImage Alpha`
- Added new `D2 Image Resize`
- Added new `D2 Resize Calculator`


<details>
<summary><strong>2024.10.24</strong></summary>

- Added new `D2 Regex Replace`
- Added new `D2 Folder Image Queue`
- `D2 Load Image`: Added image path input
- `D2 KSampler(Advanced)`: Added Positive / Negative Conditioning to Input
</details>


<details>
  <summary><strong>2024.10.19</strong></summary>

- Added `D2 Queue Button`

</details>

<details>
  <summary><strong>2024.10.18</strong></summary>

- `D2 Size Selector`: Added ability to get size from images
- `D2 Size Selector`: Added option to choose between "rounding" and "floor" for resizing

</details>

<details>
<summary><strong>2024.10.14</strong></summary>

- `D2 Load Image`: Fixed error when loading images without Exif data (e.g., pasted from clipboard)

</details>

<details>
  <summary><strong>2024.10.11</strong></summary>

- `D2 Regex Switcher`: Added ability to specify separator character for string concatenation

</details>

<details>
  <summary><strong>2024.10.10</strong></summary>

- `D2 Load Image`: Added "Open Mask Editor" button

</details>

<details>
  <summary><strong>2024.10.08</strong></summary>
  
  - Added new `D2 Load Image`

</details>

<details>
  <summary><strong>2024.10.03</strong></summary>

- `D2 Regex Switcher`: Fixed bug where matches were being passed through without processing

</details>

<details>
  <summary><strong>2024.10.02</strong></summary>

- Created by integrating existing nodes

</details>
