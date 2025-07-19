<img src="../img/title.jpg" style="max-width:100%">



<a href="../en/index.md">English</a> | <a href="../ja/index.md">日本語</a> | <a href="../zh/index.md">繁体中文</a>

- <a href="index.md">Top</a>
- <a href="node.md">Node</a> / <a href="node_image.md">Image Node</a> / <a href="node_text.md">Text Node</a> / <a href="node_xy.md">XYPlot Node</a> / <a href="node_float.md">Float Palet</a>
- <a href="workflow.md">Workflow</a>



# Node


## :tomato: XY Plot Node


### D2 XY Plot Easy

<figure>
<img src="../img/xyplot_easy.png">
</figure>

- A node that creates XY Plots with simplified workflow limited to KSampler parameters

#### Input

- `positive` / `negative` / `seed` / `steps` / `cfg` / `sampler_name` / `scheduler` / `denoise`
  - Settings to pass to KSampler
- `ckpt_name`
  - Setting to pass to D2 Checkpoint Loader
- `x_type` / `y_type`
  - Specify items to execute in XY Plot
  - When `STRING`, `INT`, or `FLOAT` is specified, output will be from `x_other`, `y_other`
- `x_list` / `y_list`
  - XY Plot modification contents
  - Since it's newline-separated text, input from other nodes is possible
- `auto_queue`
  - `true`: Automatically executes Queue the required number of times
  - `false`: Manually execute Queue
- `Reset index`
  - Reset index with this button when stopped midway

#### Output

- `xy_pipe`
  - Collectively outputs parameters used in D2 KSampler
- `grid_pipe`
  - Collectively outputs parameters `x_annotation` `y_annotation` `status` used in D2 Grid Image
- `positive` / `negative` / `seed` / `steps` / `cfg` / `sampler_name` / `scheduler` / `denoise`
  - Parameters to pass to KSampler
- `ckpt_name`
  - Setting to pass to D2 Checkpoint Loader
- `x_other` / `y_other`
  - Outputs from here when `x_type` `y_type` is set to `STRING` `INT` `FLOAT`
- `x_annotation` / `y_annotation`
  - Header text to connect to `D2 XY Grid Image`
- `status`
  - Control signal to connect to `D2 XY Grid Image`
- `index`
  - Current processing count

---


### D2 XY Plot

<figure>
<img src="../img/xyplot.png">
</figure>

- Node for creating versatile XY Plot workflows
- X/Y inputs are simple newline-separated text for easy combination with other nodes

#### Input

- `x_type` / `y_type`
  - Specify data type of `x_list` `y_list` from `STRING` `INT` `FLOAT`
- `x_title` / `y_title`
  - Text to add to header text
- `x_list` / `y_list`
  - XY Plot change contents
  - Newline-separated text that can be input using other nodes
- `auto_queue`
  - `true`: Automatically execute required number of Queues
  - `false`: Manually execute Queue
- `Reset index`
  - Reset index with this button when stopped midway

#### Output

- `X` / `Y`
  - Elements retrieved from `x_list` `y_list`
- `x_annotation` / `y_annotation`
  - Header text to connect to `D2 XY Grid Image`
- `status`
  - Control signal to connect to `D2 XY Grid Image`
- `index`
  - Current processing count

---

### D2 XY Grid Image

<figure>
<img src="../img/xyplot.png">
</figure>

- Grid image creation node used with `D2 XY Plot`

#### Input

- `x_annotation` / `y_annotation`
  - Header text for grid image
- `status`
  - Control text from `D2 XY Plot`
  - `INIT`: Initialize
  - `FINISH`: Output grid image
  - `{empty string}`: Other states
- `font_size`
  - Header text font size
- `grid_gap`
  - Gap between images
- `swap_dimensions`
  - `true`: Vertical grid
  - `false`: Horizontal grid
- `grid_only`
  - `true`: Output only grid image
  - `false`: Output individual images too

---

### D2 XY Prompt SR

<figure>
<img src="../img/prompt_sr_2.png">
</figure>

- Search and replace input text to pass to `D2 XY Plot`
- Can output as list

#### Input

- `prompt`
    - Prompt. Can include newlines
- `search_txt`
    - Search target text. Can include multiple words
    - Cannot use newlines
- `replace`
    - Replacement text
    - OK to include "," as it's separated by newlines

#### Output

- `x / y_list`
  - Connect to `D2 XY Plot`
- `LIST`
  - Output replaced text as list

---

### D2 XY Prompt SR2

<figure>
<img src="../img/prompt_sr2.png?3">
</figure>

- Search and replace prompts received from `D2 XY Plot` before passing to KSampler
- Use this to recreate Stable Diffusion webui A1111's Prompt S/R

#### Input

- `x_y`
  - Replacement text received from `D2 XY Plot`
- `prompt`
    - Target text for replacement
- `search`
    - Search text. Can include multiple words
    - Cannot use newlines

---

### D2 XY Seed

<figure>
<img src="../img/xy_seed.png?2">
</figure>

- Outputs random number when `-1` is specified
- Other numbers are output as-is
- Must set `x/y_type` to `INT` on `D2 XY Plot` side


---


### D2 XY Seed2

<figure>
  <img src="../img/xy_seed2.png?2">
</figure>

- A node that outputs a specified number of seed values

#### input
- `initial_number`
  - This value is used as a reference when `mode` is set to `increment`, `decrement`, or `fixed`
- `count`
  - Number of seed values to generate
- `mode`
  - `fixed`: Outputs only the `initial_number`
  - `increment`: Adds 1 to `initial_number` for each value
  - `decrement`: Subtracts 1 from `initial_number` for each value
  - `randomize`: Outputs random numbers regardless of `initial_number`

---

### D2 XY Checkpoint List / D2 XY Lora List

Removed. Please use `D2 XY Model List` instead.

---

### D2 XY Model List

<figure>
  <img src="../img/xy_model_list.png?2">
</figure>

- A node that passes Checkpoint/Lora to `D2 XY Plot`
- Useful when you want to get a large list of models but don't want to select them one by one in `D2 Checkpoint List`
- Click `get_list` to retrieve the model list, then edit it to keep only the ones you need

#### input
- `model_type`
  - Select either `checkpoints` or `loras`
- `filter`
  - Enter text to filter
  - Regular expressions are supported
  - When including `\` in search text, write it as `\\`
- `get_list`
  - Button to retrieve model list



---


### D2 XY Upload Image

<figure>
  <img src="../img/xy_upload_image.png?2">
</figure>

- A node for uploading multiple image files at once
- Files can be uploaded to a temporary folder by drag and drop
- The paths of uploaded files are displayed in the text area
- Designed to be connected to `D2 Load Image` via `D2 XY Plot Easy`


---


### D2 XY Folder Images

<figure>
<img src="../img/xy_folder_images.png">
</figure>

- Node to pass image paths from specified folder to `D2 XY Plot`

---

### D2 XY Annotation

<figure>
<img src="../img/xy_annotation.png?2">
</figure>

- Used to add headers when not using `D2 XY Plot` or when doing special XY Plot

---

### D2 XY List To Plot

<figure>
  <img src="../img/xy_list_to_plot.png?2">
</figure>

- Converts output from list nodes to be compatible with `D2 XY Plot`
- Internally, it simply performs `"\n".join(list)`, so if the list contents include line breaks, it may not work as intended
- Use `D2 XY String To Plot` when working with text that contains line breaks

---

### D2 XY String To Plot

<figure>
  <img src="../img/xy_string_to_plot.png">
</figure>

- Converts multiline text to be compatible with `D2 XY Plot` / `D2 XY Plot Easy`
- Used when you want to perform XY Plot comparisons of entire prompts
- When using with `D2 XY Plot Easy` for prompt comparison, set `x/y_type` to `STRING` and connect `x/y_other` to the `positive` input of `D2 KSampler`
