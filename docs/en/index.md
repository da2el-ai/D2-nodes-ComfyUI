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
- <a href="node.md#D2-Load-Diffusion-Model">`D2 Load Diffusion Model`</a>
  - Load Diffusion Model that outputs full model file paths
- <a href="node.md#D2-Controlnet-Loader">`D2 Controlnet Loader`</a>
  - Controlnet Loader that creates simple workflows when connected to D2 KSampler. Also supports Anima-LLLite
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

### Other Node

- <a href="node.md#D2-Model-and-CLIP-Merge-SDXL">`D2 Model and CLIP Merge SDXL`</a>
  - A node that combines ModelMergeSDXL and CLIPMergeSimple
- <a href="node.md#D2-Any-Delivery">`D2 Any Delivery`</a>
  - Node for passing multiple elements together. Backward compatible with ComfyUI-0246's Highway
- <a href="node.md#D2-Preset-Selector">`D2 Preset Selector`</a>
  - Define presets of multiple parameters as text and output a whole set from a dropdown
- <a href="node.md#D2-Save-Audio-Eagle">`D2 Save Audio Eagle`</a>
  - Save audio files to Eagle

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
- <a href="node_text.md#D2-Prompt-Sanitizer">`D2 Prompt Sanitizer`</a>
  - Cleans up prompt strings (convert `_` to space, add a space after commas)



### Image

- <a href="node_image.md#D2-Preview-Image">`D2 Preview Image`</a>
  - Image preview with gallery functionality
- <a href="node_image.md#D2-Save-Image">`D2 Save Image`</a>
  - Image saving with gallery functionality
- <a href="node_image.md#D2-Save-Image-Eagle">`D2 Save Image Eagle`</a>
  - `D2 Save Image` with Eagle registration functionality
- <a href="node_image.md#D2-Send-File-Eagle">`D2 Send File Eagle`</a>
  - Registers files at the specified path to Eagle
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
- <a href="node_xy.md#D2-XY-Model-List">`D2 XY Model List`</a>
  - Outputs a list of Checkpoints / Loras
- <a href="node_xy.md#D2-XY-Folder-Images">`D2 XY Folder Images`</a>
  - Outputs list of files in folder
- <a href="node_xy.md#D2-XY-Upload-Image">`D2 XY Upload Image`</a>
  - Upload multiple images by drag and drop
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
- <a href="node_float.md#D2-Progress-Preview">`D2 Progress Preview`</a>
  - A palette that displays images during generation



## :blossom: Changelog

**2026.06.15**

- `D2_CutByMask`: Added `round_to` to round up the cut rectangle to a unit such as 8px
- `D2_EmptyImageAlpha`: Added `output_alpha` to output RGB without an alpha channel

**2026.06.10**

- `D2_PromptSanitizer`: Added `remove_extra_comma` to clean up redundant commas

**2026.06.08**

- `D2_PromptSanitizer`: Newly added

**2026.06.03**

- `D2_ControlnetLoader` / `D2_KSampler`: Added support for MASK input

**2026.05.29**

- `D2_PresetSelector`: Added new node
- `D2_PresetSelector`: Added a `preset_name` input (lets you switch presets from outside) and a sample default for `preset_text`
- `D2_ControlnetLoader` / `D2_KSampler`: Added support for kohya-ss's Anima-LLLite. Added a `controlnet_type` input (requires [ComfyUI-Anima-LLLite](https://github.com/kohya-ss/ComfyUI-Anima-LLLite))

**2026.04.13**

- `D2_SaveAudioEagle`: Added new node

**2026.03.09**

- `D2_XY_ModelList`: Added support for retrieving the "diffusion_models" list

**2026.03.03**

- `D2 KSampler` / `D2 KSampler Advanced`: Fixed to reflect KSampler values when d2_pipe contents are empty

**2026.0２.13**

- `D2 Prompt`: Changed to a toggle switch to allow disabling token count
- `D2 Load Diffusion Model`: Added new node

**2026.01.16**

- `D2 XYPlot Easy Mini`: Fixed an issue where an error could occur when loading and running a `D2 XYPlot Easy` workflow

**2025.10.25**

- `D2_FilenameTemplate`: add filename sanitization option

**2025.10.13**

- `Prompt Convert`: Close dialog when prompt is copied

**2025.10.09**

- `D2_SaveImage` / `D2_SaveImageEagle`: Changed to not save workflows in JPEG/WEBP format. This is because when workflows or prompts become lengthy, they exceed the Exif capacity limit and cannot be saved.

**2025.09.22**

- `D2_KSampler`: Modified to override positive and negative prompts in d2_pipe when prompts are specified in positive and negative parameters

**2025.09.14**

- `D2_SaveImage` / `D2_SaveImageEagle`: Added A1111-style generation parameters to metadata
- `D2_SaveImageEagle`: When d2_pipe is connected, A1111-style memo is automatically created
- `D2_LoadImage`: Added support for outputting prompts saved with "Save Image With Prompt" and "Save Image w/Metadata"

**2025.08.20**

- `D2_FilenameTemplate` / `D2_FilenameTemplate2`: Support for retrieving values from arrays, dictionaries, and objects
- `D2_FilenameTemplate` / `D2_FilenameTemplate2`: Added preset feature
- `D2_KSampler` / `D2_KSamplerAdvanced`: Register width / height to d2_pipe

**2025.08.10**

- `D2 Any Delivery`: Added new node

**2025.08.09**

- `D2_KSampler`: Added support for Qwen-Image latent

**2025.08.07**

- `D2_SaveImageEagle` / `D2_SendFileEagle`: Newly added

**2025.08.06**

- `D2_FilenameTemplate` / `D2_FilenameTemplate2`: Added feature to increase/decrease input items. Added seed
- Updated several sample workflows

**2025.08.05**

- `D2_SaveImage`: Added support for WEBP, animated WEBP, and JPEG formats

**2025.07.19**

- `D2_CheckpointList` / `D2_LoraList`: Removed
- `D2_ImageResize`: Added rotation functionality. Also supports masks

**2025.06.22**

- `D2_SaveImage`: Newly added

**2025.06.19**

- `D2_PromptConvert`: Support new weight format for NovelAI4

<details>
<summary><strong>2025.05.02</strong></summary>

- `D2_ProgressPreview`: Newly added.
- `D2_XYUploadImage`: Newly added.

</details>


<details>
<summary><strong>2025.04.30</strong></summary>

- `D2_FolderImageQueue` `D2_FolderImages` `D2_LoadFolderImages`: Added sorting functionality

</details>


<details>
<summary><strong>2025.04.28</strong></summary>

- `D2_FolderImageQueue`: Changed start number from `1` to `0`

</details>


<details>
<summary><strong>2025.04.24</strong></summary>

- `D2_FilenameTemplate2`: Newly added. Multiple line support version of `D2_FilenameTemplate`
- `D2 EmptyImage Alpha` color specification changed to red green blue. Color samples also added

</details>


<details>
<summary><strong>2025.04.22</strong></summary>

- `D2_CutByMask`: Added `square_thumb` mode to cut with maximum-sized square
- `D2_XYFolderImages` / `D2_LoadFolderImages`: Changed to update the image list every time. Added display of image count
- `D2_LoadImage`: Fixed a bug where prompts from PNG images created in A1111 were not being output

</details>


<details>
<summary><strong>2025.04.18</strong></summary>

- `D2_KSamplerAdvanced`: Added parameters `weight_interpretation` and `token_normalization` to adjust prompt weights
  - Requires [Advanced CLIP Text Encode](https://github.com/BlenderNeko/ComfyUI_ADV_CLIP_emb/) to use.

</details>


<details>
<summary><strong>2025.04.16</strong></summary>

- `D2_Prompt`: Add LoRA insertion button
- `D2_KSampler` / `D2_KSamplerAdvanced`: Support A1111-style LoRA loading prompts. Load LoRA inside KSampler
- `D2_LoadLora`: Changed the output `prompt` to output A1111-style LoRA loading prompts without removing them. The conventional output has been renamed to `formatted_prompt`

</details>


<details>
<summary><strong>2025.04.14</strong></summary>

- `D2 Cut By Mask`: Newly added
- `D2 Paste By Mask`: Newly added
- `D2 XY Model List`: Added support for upscaler models
- `D2 KSampler Advanced`: Added d2_pipe to outputs

</details>


<details>
<summary><strong>2025.04.09</strong></summary>

- `D2_LoadImage`: Added output of filename and file path
- `D2_FilenameTemplate`: Added tooltip to `format` (displayed on mouse hover)

</details>


<details>
<summary><strong>2025.04.06</strong></summary>

- `D2 Image Mask Stack`: Newly added
- `D2 Mosaic Filter`: Newly added

</details>


<details>
<summary><strong>2025.04.02</strong></summary>

- `D2 Prompt`: Newly added
- `D2 Delete Comment`: Integrated into `D2 Prompt`

</details>


<details>
<summary><strong>2025.03.31</strong></summary>

- `D2 Token Counter`: Newly added

</details>


<details>
<summary><strong>2025.03.25</strong></summary>

- Added comment shortcut key (ctrl + /)
- `D2 XYPlot Easy Mini`: Added a version of `D2 XYPlot Easy` with limited output slots

</details>


<details>
<summary><strong>2025.03.23</strong></summary>

- `D2 Delete Comment`: Newly added
- `D2 Load Lora`: Added option to enable the use of A1111 format
- `D2 Model List`: Added option to retrieve in A1111 format

</details>


<details>
<summary><strong>2025.02.27</strong></summary>

- `D2 Load Lora`: Newly added
- `D2 Multi Output`: Added x_list/ylist output

</details>


<details>
<summary><strong>2025.02.23</strong></summary>

- `D2 Model and CLIP Merge SDXL`: Added checkpoint merge nodes

</details>


<details>
<summary><strong>2025.01.20</strong></summary>

- `D2 XY Seed2`: Added new node
- `D2 XY Plot / D2 XY Plot Easy`: Added ability to specify XY plot starting position
- `D2 XY Plot / D2 XY Plot Easy`: Added estimated time remaining display for XY plots
- `D2 Regex Replace`: Added support for using whitespace in replacement strings

</details>


<details>
<summary><strong>2024.12.28</strong></summary>

- `D2 Pipe`: Added new node
- `D2_KSampler / D2_XYPlotEasy`: Changed xy_pipe name to d2_pipe

</details>


<details>
<summary><strong>2024.12.18</strong></summary>

- `D2 Filename Template`: Added new node
- `D2 Grid Image`: Added the ability to specify the grid image output trigger by the number of images

</details>


<details>
<summary><strong>2024.12.16</strong></summary>

- `D2 XY String To Plot`: Added new node
- `D2 XY Grid Image`: Added support for line breaks in labels
- `D2 XY Grid Image`: Added option to toggle label output
- `D2 XY Prompt SR`: Added support for text containing line breaks
- `D2 XY Plot Easy`: Modified to record random values in `x/y_annotation` when `-1` is specified for seed

</details>


<details>
<summary><strong>2024.12.14</strong></summary>

- `D2 KSampler`: Added `xy_pipe` for connection with `D2 XY Plot Easy`
- `D2 Grid Image`: Added `grid_pipe` for connection with `D2 XY Plot` and `D2 XY Plot Easy`
- `D2 XY Plot Easy`: Newly added
- `D2 XY Model List`: Added filename and date sorting. Added support for retrieving Sampler and Scheduler lists

</details>


<details>
<summary><strong>2024.12.05</strong></summary>

- Added Conditioning output to `D2 KSampler` / `D2 KSampler`

</details>


<details>
<summary><strong>2024.11.27</strong></summary>

- Added new `D2 Preview Image`

</details>


<details>
<summary><strong>2024.11.23</strong></summary>

- Added new `D2 Model List`

</details>


<details>
<summary><strong>2024.11.21</strong></summary>

- `D2 Checkpoint Loader`: Added settings for Vpred (v_prediction)
- `D2 Image Resize`: Modified to enable Latent output

</details>


<details>
<summary><strong>2024.11.20</strong></summary>

- `D2 Image Resize`: Added support for upscale models (like SwinIR_4x)

</details>


<details>
<summary><strong>2024.11.18</strong></summary>

- Added many nodes at once
- Added `D2 Controlnet Loader`, `D2 Get Image Size`, `D2 Grid Image`, `D2 Image Stack`, `D2 List To String`, `D2 Load Folder Images`
- Added XY Plot related nodes
- Added `D2 XY Annotation`, `D2 XY Checkpoint List`, `D2 XY Folder Images`, `D2 Grid Image`, `D2 XY List To Plot`, `D2 XY Lora List`, `D2 XY Plot`, `D2 XY Prompt SR`, `D2 XY Prompt SR2`, `D2 XY Seed`
- Existing nodes have also been modified, see commit history for details

</details>


<details>
<summary><strong>2024.11.02</strong></summary>

- `D2 Regex Switcher`: Added toggle for input text confirmation textarea

</details>


<details>
<summary><strong>2024.10.28</strong></summary>

- Added `Prompt convert`: Dialog for converting prompts between NovelAI and StableDiffusion
- `D2 Folder Image Queue`: Fixed issue where image generation count was inconsistent

</details>


<details>
<summary><strong>2024.10.26</strong></summary>

- Added new `D2 EmptyImage Alpha`
- Added new `D2 Image Resize`
- Added new `D2 Resize Calculator`

</details>


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
