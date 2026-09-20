# D2 Create Masks

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/create_masks.png">
</figure>

- Node that creates multiple masks by dragging rectangles on a canvas
- Drag inside a rectangle to move it, drag the white circles at its corners to resize it
- Rectangles increase or decrease with `mask_count`, and the `mask_1` `mask_2` ... outputs follow along
- Dropping an image onto the node shows it as the canvas background and applies its size to `width` / `height`

## Input

- `mask_count`
  - Number of masks (1-16). The number of `mask_N` outputs follows this value
- `select_mask`
  - Number of the mask to make active. It changes automatically to the number of the mask you click on the canvas
- `width` / `height`
  - Size of the output masks. It also determines the aspect ratio of the canvas
- `image`
  - Image shown in the background. Leave it empty for a black canvas
- `masks`
  - JSON of the mask positions and sizes. It updates automatically when you drag, so you normally don't need to touch it

## Output

- `image`
  - The specified image. If no image is specified, a black image of `width` x `height`
- `width` / `height`
  - Size of the masks
- `mask_1`
  - Mask 1. If `mask_count` is "3", `mask_2` `mask_3` are also output

## About the active mask

The mask you click becomes "active": it is shown in front of the others and white circles for resizing appear at its corners.

When masks overlap completely you cannot click the one underneath, so pick its number with `select_mask` instead. Conversely, changing the active mask by clicking also updates `select_mask`.
