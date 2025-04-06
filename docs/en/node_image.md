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

- `IMAGE / MASK`
    - Image and mask
- `width / height`
    - Image size
- `positive` / `negative`
    - Prompts

Note: Prompts may not be retrievable depending on workflow configuration. For example, they cannot be retrieved without a node containing the string "KSampler" (e.g., Tiled KSampler).

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

