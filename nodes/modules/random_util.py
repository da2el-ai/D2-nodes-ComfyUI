"""
D2 Random Mask / D2 Random Point の乱数計算。
ComfyUI 非依存にして単体テスト（test/test_random_util.py）できるようにする。

乱数生成器（random.Random インスタンス）は引数で受け取る。
グローバルの random を触ると同じワークフロー内の他ノードの結果まで引きずられるうえ、
テストでシードを固定した検証もできなくなるため。
"""
from .marker_util import MODE_ABSOLUTE, MODE_RELATIVE, MODES


# 座標の出力数値型。absolute のときだけ効く（relative は常に float）
NUMBER_TYPE_INT = "int"
NUMBER_TYPE_FLOAT = "float"
NUMBER_TYPES = [NUMBER_TYPE_INT, NUMBER_TYPE_FLOAT]


"""
min / max を (下限, 上限) の順に並べ替える。
逆転して入力されてもエラーにせず、入れ替えて扱う。
"""
def sort_range(min_value, max_value):
    if min_value > max_value:
        return max_value, min_value
    return min_value, max_value


"""
0.0〜1.0 の相対値を一様乱数で1つ返す。
範囲は 0.0〜1.0 にクランプする（ウィジェットでも制限するが、
上流ノードからの入力もありうるのでここでも守る）。
"""
def random_relative(rng, min_value, max_value):
    lo, hi = sort_range(float(min_value), float(max_value))
    lo = min(1.0, max(0.0, lo))
    hi = min(1.0, max(0.0, hi))
    return rng.uniform(lo, hi)


"""
長方形の一辺の長さ（ピクセル）を乱数で1つ返す。
1〜limit にクランプするので、limit を超える長さにはならない。
両端を含む（randint）。
"""
def random_size(rng, min_value, max_value, limit):
    lo, hi = sort_range(int(min_value), int(max_value))
    lo = min(limit, max(1, lo))
    hi = min(limit, max(1, hi))
    return rng.randint(lo, hi)


"""
width × height の内側に収まる長方形をランダムに1つ作る。
返すのは {"x", "y", "w", "h"} のピクセル値（int）。

先に幅・高さを決めてから、はみ出さない範囲で左上座標を選ぶ。
これで x + w <= width / y + h <= height が必ず成立する。
位置の分布は一様（中央寄せなどの重み付けはしない）。
"""
def random_rect(rng, width, height, min_w, max_w, min_h, max_h):
    w = random_size(rng, min_w, max_w, width)
    h = random_size(rng, min_h, max_h, height)
    return {
        "x": rng.randint(0, width - w),
        "y": rng.randint(0, height - h),
        "w": w,
        "h": h,
    }


"""
相対値（0.0〜1.0）を座標の出力値へ変換する。

absolute + int   → int(round(rel * size))。値域は 0〜size（両端を含む）
absolute + float → float(rel * size)
relative         → float(rel)。number_type は無視する
                   （int に丸めると 0 か 1 にしかならず無意味なため）

absolute + int の値域は marker_util.to_output_value と揃えてある。
ピクセルインデックス（0〜size-1）が要る下流は受け側で調整する前提。
"""
def to_point_value(rel, size, mode, number_type):
    if mode != MODE_ABSOLUTE:
        return float(rel)

    if number_type == NUMBER_TYPE_FLOAT:
        return float(rel * size)

    return int(round(rel * size))
