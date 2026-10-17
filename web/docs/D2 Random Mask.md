# D2 Random Mask

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/random_mask.png">
</figure>

- Node that outputs a random rectangular mask
- The rectangle is placed so that it never extends beyond `width` / `height`

## Input

- `width` / `height`
  - Size of the output mask
- `min_width` / `max_width`
  - Range of the rectangle width (pixels)
- `min_height` / `max_height`
  - Range of the rectangle height (pixels)
- `seed`
  - Random seed. The same value gives the same rectangle

## Output

- `width` / `height`
  - The mask size you entered is output as is
- `mask`
  - Mask that is white inside the rectangle
- `mask_x` / `mask_y`
  - Top-left coordinates of the rectangle
- `mask_w` / `mask_h`
  - Width and height of the rectangle

## About the rectangle size

Entering the same value for `min_width` and `max_width` fixes the width, so only the position moves randomly.

When `max` is smaller than `min` the two are swapped, and a size larger than `width` / `height` is reduced to the mask size. The rectangle never extends outside the mask.
