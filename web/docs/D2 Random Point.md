# D2 Random Point

<figure>
  <img src="https://raw.githubusercontent.com/da2el-ai/D2-nodes-ComfyUI/refs/heads/main/docs/img/random_point.png">
</figure>

- Node that outputs random XY coordinates
- You can limit the range by setting min / max

## Input

- `width` / `height`
  - Size of the coordinate system
- `min_x` / `max_x`
  - Range of the X coordinate
- `min_y` / `max_y`
  - Range of the Y coordinate
- `mode`
  - `absolute`: Outputs actual pixel coordinates
  - `relative`: Outputs a relative value from 0.0 to 1.0
- `number_type`
  - `int` / `float`. It only takes effect when `mode` is `absolute`
- `seed`
  - Random seed. The same value gives the same coordinates

## Output

- `width` / `height`
  - The size of the coordinate system you entered is output as is
- `x` / `y`
  - The randomly chosen coordinates

## About the range

`min_x` `max_x` `min_y` `max_y` are always specified as relative values from 0.0 to 1.0, regardless of `mode`.

For example, setting `min_x` to `0.25` and `max_x` to `0.75` keeps the coordinates near the center. Changing `width` does not change what "near the center" means.

Entering the same value for `min` and `max` fixes the coordinate at that position.

## About number_type

When `mode` is `absolute`, `int` outputs an integer like `100` and `float` outputs a decimal like `100.3968`.

`relative` is a range from 0 to 1, so it is always a decimal.
