"""
D2 Create Masks の長方形マスク計算。
ComfyUI 非依存にして単体テスト（test/test_mask_rect_util.py）できるようにする。

矩形は常に相対値（0.0〜1.0）で保持する。x / y は左上、w / h は幅・高さ。
こうすると width / height を変えてもマスクが画面上で動かない。
ピクセルへの変換は出力時にだけ行う。
"""
import json


# マスクの最大数。これを超えると出力が増えすぎてノードが実用的でなくなる
MAX_MASK_COUNT = 16

# 既定の幅・高さ（相対値）。キャンバスの 1/4
DEFAULT_MASK_SIZE = 0.25

# 既定位置の左上（相対値）。DEFAULT_MASK_SIZE と合わせて中心が 0.5, 0.5 になる
DEFAULT_MASK_ORIGIN = 0.375

# 番号ごとに既定位置をずらす幅（相対値）。既定のままでも完全に重ならないようにする
MASK_OFFSET_STEP = 0.02

# 最小の幅・高さ（相対値）。潰れて掴めなくなるのを防ぐ
MIN_MASK_SIZE = 0.01


"""
マスクの既定矩形（相対値）を返す。中央 1/4 サイズを番号ごとに右下へずらす。
web/D2_CreateMasks.js も同じ式で既定矩形を作ること。
ここがズレると、実行するまで気づかないマスク位置の食い違いになる。

D2 Create Point の default_marker_position と違い count を取らない。
mask_count を増減しても既存マスクの既定位置が動かないようにするため。
"""
def default_mask_rect(index):
    offset = index * MASK_OFFSET_STEP
    return {
        "x": DEFAULT_MASK_ORIGIN + offset,
        "y": DEFAULT_MASK_ORIGIN + offset,
        "w": DEFAULT_MASK_SIZE,
        "h": DEFAULT_MASK_SIZE,
    }


"""
数値として扱い、min_value〜max_value に収める。扱えなければ None を返す。
"""
def _clamp(value, min_value, max_value):
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    return min(max_value, max(min_value, num))


"""
矩形1件を正規化する。取り出せなければ既定矩形。

はみ出した分は位置を内側へ押し戻して吸収し、幅・高さは縮めない。
掴んで端へ運んだときにサイズまで変わるほうが驚きが大きいため。
"""
def normalize_rect(rect, index):
    if not isinstance(rect, dict):
        return default_mask_rect(index)

    x = _clamp(rect.get("x"), 0.0, 1.0)
    y = _clamp(rect.get("y"), 0.0, 1.0)
    w = _clamp(rect.get("w"), MIN_MASK_SIZE, 1.0)
    h = _clamp(rect.get("h"), MIN_MASK_SIZE, 1.0)

    if x is None or y is None or w is None or h is None:
        return default_mask_rect(index)

    return {
        "x": min(x, 1.0 - w),
        "y": min(y, 1.0 - h),
        "w": w,
        "h": h,
    }


"""
パース済みリストの index 番目を正規化する。取り出せなければ既定矩形。
"""
def _rect_at(parsed, index):
    if index >= len(parsed):
        return default_mask_rect(index)
    return normalize_rect(parsed[index], index)


"""
masks の JSON をパースして count 件の矩形リストにする。
壊れた JSON・配列でない・要素不足・要素が不正なら既定矩形で補う。
要素が count を超える場合は先頭 count 件だけ使う
（余剰要素は JSON 側に残す。mask_count を減らして戻したとき矩形を復元するため）。
"""
def parse_masks(masks_json, count):
    try:
        parsed = json.loads(masks_json)
    except (ValueError, TypeError):
        parsed = None

    if not isinstance(parsed, list):
        parsed = []

    return [_rect_at(parsed, i) for i in range(count)]


"""
1軸ぶんの相対値をピクセル範囲（半開区間）に変換する。
丸めやクランプで幅が 0 になったら最低1ピクセルを確保する。
0ピクセルの空マスクは下流でエラーになるだけで嬉しくない。
"""
def _axis_to_pixels(start, size, length):
    p0 = min(max(int(round(start * length)), 0), length)
    p1 = min(max(int(round((start + size) * length)), 0), length)

    if p1 <= p0:
        p0 = min(p0, length - 1)
        p1 = p0 + 1

    return p0, p1


"""
相対矩形をピクセル範囲 (x0, y0, x1, y1) に変換する。
x1 / y1 は含まない半開区間で、そのままテンソルのスライスに使える。
"""
def rect_to_pixels(rect, width, height):
    x0, x1 = _axis_to_pixels(rect["x"], rect["w"], width)
    y0, y1 = _axis_to_pixels(rect["y"], rect["h"], height)
    return x0, y0, x1, y1
