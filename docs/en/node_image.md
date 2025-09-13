<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



# Node

## :tomato: Image Node


### D2 Preview Image

<figure>
<img src="../img/preview_image_1.png">
<img src="../img/preview_image_2.png">
</figure>

- Click the `Popup Image` button to display the full-screen gallery

---

### D2 Save Image

<figure>
<img src="../img/save_image_2.png?2">
</figure>

- An image saving node with full-screen gallery functionality, similar to `D2 Preview Image`
- Supports PNG / JPEG / WEBP / animated WEBP image formats
- Saves A1111-style generation parameters to metadata
- When loaded with `D2 Load Image`, positive and negative prompts can be extracted from saved images

#### Input

- `images`: Images to save
- `d2_pipe`: Receives generation parameters from `D2 KSampler` etc.
- `filename_prefix`: Filename format. See <a href="node_text.md#D2-Filename-Template">`D2 Filename Template`</a> for details
- `preview_only`:
  - `true`: Only preview images without saving
  - `false`: Save images
- `format`: Select image format from `png` / `jpeg` / `webp` / `animated_webp`
- `lossless`: Applied for `webp` and `animated_webp`
  - `true`: Lossless compression
  - `false`: Lossy compression
- `quality`: Image compression ratio. Applied for `jpeg` or `webp`, `animated_webp` with `lossless:false`
- `fps`: Frame rate for `animated_webp`
- `Popup Image`: Clicking the button displays a full-screen gallery

#### Output

- `filenames`: Array of full paths of saved image files

---

### D2 Save Image Eagle

<figure>
<img src="../img/save_image_eagle.png?2">
</figure>

- `D2 Save Image` with Eagle registration functionality
- <a href="https://eagle.cool/" target="_blank">Eagle Official Website</a>

#### Differences from `D2 Send Eagle`

- Supports animated WEBP
- Full-screen gallery functionality
- Filename rules conform to the standard `Save Image`
- Tag saving feature excluded
- Generation parameter memos can be freely created
  - Need to be created using tools like `D2 Filename Template2`
  - As various generation environments like videos and Flux have increased, existing generation parameter saving methods have become inadequate

#### Input

- `eagle_folder`: Eagle registration folder. Can use either folder name or folder ID
- `memo_text`: Text to register as a memo in Eagle

#### Recording A1111 webui-style parameters in Eagle memo

<figure>
<img src="../img/save_image_eagle_3.png?2">
</figure>

Use `D2 Filename Template2` to create a template and input it into the `memo_text` of `D2 Save Image Eagle`.

In the sample above, `positive` and `negative` from `D2 KSampler` are input to `arg_1` and `arg_2` and retrieved with `%arg_1%` and `%arg_2%`, while other parameters are retrieved with `%{Node name}.{Param}`.

For details on parameter retrieval methods, see <a href="node_text.md#D2-Filename-Template">`D2 Filename Template`</a>.

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

---

### D2 Send File Eagle

<figure>
<img src="../img/send_file_eagle.png?2">
</figure>

- Registers files at the path input in `file_path` to <a href="https://eagle.cool/" target="_blank">Eagle</a>
- Created to register output files from `Video Combine` to Eagle
- Can also save video generation parameters by using `D2 File Template2` for `memo_text` input

##### About file_path

Provide the full path of the file as a string or an array of strings.

Example: String
```
D:\ComfyUI\output\foo.png
```
Example: Array of strings
```
["D:\ComfyUI\output\foo.png","D:\ComfyUI\output\bar.png"]
```

##### About Filenames output by Video Combine

The `Filenames` output by <a href="https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite" target="_blank">Video Combine</a> is an array like the following:

```
[
  true, 
  [
    "D:\\ComfyUI\\output\\AnimateDiff_00002.png",
    "D:\\ComfyUI\\output\\AnimateDiff_00002.mp4"
  ]
]
```

In the image above, the `Exec` node from <a href="https://github.com/godmt/ComfyUI-List-Utils" target="_blank">ComfyUI-List-Utils</a> is used to extract the filename part.


### D2 Load Image

<figure>
<img src="../img/load_image.png">
</figure>

- Load Image node that can extract prompts from images
- Compatible with images created in StableDiffusion webui A1111 and NovelAI
- Includes a button to open mask editor

#### Input

- `image_path`
  - Loads file when image path is input
  - Used for connection with `D2 Folder Image Queue`

#### Output

- `IMAGE / MASK`: Image and mask
- `width / height`: Image size
- `positive` / `negative`: Prompts
- `filename` / `filepath`: Name and path of the saved file
- `pnginfo`: Image metadata

#### About Prompt Output

Compatible with images saved by the following nodes and UIs:

- `D2 Save Image`, `D2 Save Image Eagle`
- <a href="https://github.com/easygoing0114/ComfyUI-easygoing-nodes?tab=readme-ov-file" target="_blank">Save Image With Prompt</a>
- <a href="https://github.com/giriss/comfy-image-saver" target="_blank">Save Image w/Metadata</a>
- Novel AI
- A1111 (including Forge variants)

---

### D2 Load Folder Images

<figure>
<img src="../img/load_folder_images.png">
</figure>

- Batch loads and outputs images from a folder
- Used with `D2 Grid Image` etc.
- Use `D2 Folder Image Queue` for sequential processing

#### Input

- `folder`
  - Specify folder in full path
- `extension`
  - Specify like `*.jpg` to load only JPEG images
  - Can also specify patterns like `*silver*.webp`

---

### D2 Folder Image Queue

<figure>
<img src="../img/folder_image_queue_2.png">
</figure>

- Outputs paths of images in a folder
- Automatically executes Queue for the number of images when Queue is run

#### Input

- `folder`
  - Image folder
- `extension`
  - Specify file name filter
  - `*.*`: All images
  - `*.png`: PNG format only
- `start_at`
  - Image number to start processing
- `auto_queue`
  - `true`: Automatically execute remaining Queues
  - `false`: Execute only once

#### Output

- `image_path`
  - Full path of image

---

### D2 Grid Image

<figure>
<img src="../img/grid_image.png">
</figure>

- Outputs grid images
- Supports both horizontal and vertical alignment

#### Input

- `max_columns`
  - Number of images to align horizontally
  - When `swap_dimensions` is `true`, this becomes the number of vertical images
- `grid_gap`
  - Spacing between images
- `swap_dimensions`
  - `true`: Vertical alignment
  - `false`: Horizontal alignment
- `trigger_count`
  - Outputs grid image when the number of input images reaches this specified value
- `Image count`
  - Number of input images
- `Reset Images`
  - Discards all input images


---

### D2 Image Stack

<figure>
<img src="../img/image_stack.png">
</figure>

- Combines multiple input images into a batch
- Can be used with D2 Grid Image and others
- Maximum of 50 inputs


---

### D2 Image Mask Stack

<figure>
<img src="../img/image_mask_stack.png">
</figure>

- Combines multiple input images and masks into a batch
- Essentially D2 Image Stack with added mask support


---

### D2 EmptyImage Alpha

<figure>
<img src="../img/empty_image_alpha.png">
</figure>

- Adds alpha channel (transparency) to EmptyImage


---


### D2 Mosaic Filter

<figure>
<img src="../img/mosaic.png">
</figure>

- Applies a mosaic filter
- Adjustable transparency, brightness, and color inversion options


---


### D2 Cut By Mask

<figure>
<img src="../img/cut-by-mask.png">
</figure>

- Cut an image using a mask
- Can specify the output shape, size, margins, etc.


#### Input

- `images`: Source image to cut from
- `mask`: Mask
- `cut_type`: Shape of the cut image
    - `mask`: Cut according to the mask shape
    - `rectangle`: Calculate and cut a rectangle from the mask shape
    - `square_thumb`: Cuts out the maximum-sized square. A mode intended for thumbnails
- `output_size`: Output image size
    - `mask_size`: Mask size
    - `image_size`: Input image size (surroundings become transparent while preserving the input image position)
- `padding`: Number of pixels to expand the mask area (default 0)
- `min_width`: Minimum width of mask size (default 0)
- `min_height`: Minimum height of mask size (default 0)
- `output_alpha`: Whether to include alpha channel in the output image

#### output
- `image`: Image cut by the mask area
- `mask`: Mask
- `rect`: Cut rectangular area



---


### D2 Paste By Mask

<figure>
<img src="../img/paste-by-mask.png">
</figure>

- Composite images using masks or rectangular areas created with D2 Paste By Mask
- Can specify blur width, paste shape, etc.

#### Input

- `img_base`: Base image (batch compatible)
- `img_paste`: Image to paste (batch compatible)
- `paste_mode`: Determines how to trim img_paste and the paste coordinates
    - `mask`: Mask img_paste with mask_opt and paste at position x=0, y=0 (mask shape pasting)
    - `rect_full`: Trim img_paste to the size of rect_opt and paste at the position of rect_opt (rectangular pasting)
    - `rect_position`: Paste img_paste at the position of rect_opt (rectangular pasting)
    - `rect_pos_mask`: Mask img_paste with mask_opt and paste at the position of rect_opt (mask shape pasting)
- `multi_mode`: Processing method when either or both of img_base and img_paste have multiple images
    - `pair_last`: Process img_base and img_paste pairs from the beginning with the same index. If one has fewer images, the last image is used
    - `pair_only`: Same as pair_last. If one has fewer images, an error is displayed and processing stops
    - `cross`: Process all combinations

input `optional`:
- `mask_opt`: Mask
- `rect_opt`: Rectangular area
- `feather`: Number of pixels to blur the edge (default 0)


#### output

- `image`: Composited image

#### About multi_mode

`pair_last` and `pair_only` output the same ordered images from `img_base` and `img_paste` as pairs.

<figure>
<img src="../img/paste-by-mask_pair.png">
</figure>

`cross` outputs all combinations.

<figure>
<img src="../img/paste-by-mask_cross.png">
</figure>
