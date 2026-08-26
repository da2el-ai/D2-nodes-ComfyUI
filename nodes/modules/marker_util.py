"""
D2 Create Point のマーカー座標計算。
ComfyUI 非依存にして単体テスト（test/test_marker_util.py）できるようにする。

マーカー座標は mode に関わらず常に相対値（0.0〜1.0）で保持する。
こうすると mode を切り替えても、width / height を変えてもマーカーが画面上で動かない。
絶対値への変換は出力時にだけ行う。
"""
import json


# 座標の出力モード
MODE_ABSOLUTE = "absolute"
MODE_RELATIVE = "relative"
MODES = [MODE_ABSOLUTE, MODE_RELATIVE]

# マーカーの最大数。これを超えると出力が増えすぎてノードが実用的でなくなる
MAX_MARKER_COUNT = 16


def default_marker_position(index, count):
    """
    マーカーの既定位置（相対値）を返す。左から等間隔・縦は中央。
    web/D2_CreatePoint.js も同じ式で既定位置を作ること。
    ここがズレると、実行するまで気づかない座標の食い違いになる。
    """
    return {"x": (index + 1) / (count + 1), "y": 0.5}


def _clamp01(value):
    """0.0〜1.0 に収める。数値として扱えなければ None を返す。"""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    return min(1.0, max(0.0, num))


def _marker_at(parsed, index, count):
    """パース済みリストの index 番目を正規化する。取り出せなければ既定位置。"""
    default = default_marker_position(index, count)

    if index >= len(parsed):
        return default

    item = parsed[index]
    if not isinstance(item, dict):
        return default

    x = _clamp01(item.get("x"))
    y = _clamp01(item.get("y"))
    if x is None or y is None:
        return default

    return {"x": x, "y": y}


def parse_markers(markers_json, count):
    """
    markers の JSON をパースして count 件の座標リストにする。
    壊れた JSON・配列でない・要素不足・要素が不正なら既定位置で補う。
    要素が count を超える場合は先頭 count 件だけ使う
    （余剰要素は JSON 側に残す。marker_count を減らして戻したとき位置を復元するため）。
    """
    try:
        parsed = json.loads(markers_json)
    except (ValueError, TypeError):
        parsed = None

    if not isinstance(parsed, list):
        parsed = []

    return [_marker_at(parsed, i, count) for i in range(count)]


def to_output_value(rel, size, mode):
    """
    相対値（0.0〜1.0）を出力値へ変換する。
    absolute は round(rel * size) の int で、値域は 0〜size（両端を含む）。
    ピクセルインデックス（0〜size-1）が要る下流は受け側で調整する前提。
    """
    if mode == MODE_ABSOLUTE:
        return int(round(rel * size))
    return float(rel)


def markers_to_outputs(markers, width, height, mode):
    """
    マーカーのリストを x_1, y_1, x_2, y_2, ... の平坦なリストにする。
    """
    values = []
    for marker in markers:
        values.append(to_output_value(marker["x"], width, mode))
        values.append(to_output_value(marker["y"], height, mode))
    return values
