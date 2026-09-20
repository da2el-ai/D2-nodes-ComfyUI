import sys
import os
import json
import unittest

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.mask_rect_util import (
    MAX_MASK_COUNT,
    MIN_MASK_SIZE,
    default_mask_rect,
    normalize_rect,
    parse_masks,
    rect_to_pixels,
)


class TestDefaultMaskRect(unittest.TestCase):
    def test_first_rect_is_centered(self):
        """1個目は中央に置かれる"""
        rect = default_mask_rect(0)
        self.assertAlmostEqual(rect["x"] + rect["w"] / 2, 0.5)
        self.assertAlmostEqual(rect["y"] + rect["h"] / 2, 0.5)

    def test_offset_by_index(self):
        """番号ごとに右下へずれる"""
        first = default_mask_rect(0)
        second = default_mask_rect(1)
        self.assertGreater(second["x"], first["x"])
        self.assertGreater(second["y"], first["y"])

    def test_all_rects_fit_in_canvas(self):
        """上限の番号まで 0.0〜1.0 に収まる"""
        for index in range(MAX_MASK_COUNT):
            rect = default_mask_rect(index)
            self.assertGreaterEqual(rect["x"], 0.0)
            self.assertGreaterEqual(rect["y"], 0.0)
            self.assertLessEqual(rect["x"] + rect["w"], 1.0)
            self.assertLessEqual(rect["y"] + rect["h"], 1.0)


class TestNormalizeRect(unittest.TestCase):
    def test_valid_rect_passes_through(self):
        """正常な矩形はそのまま通る"""
        rect = normalize_rect({"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4}, 0)
        self.assertEqual(rect, {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4})

    def test_not_dict_falls_back_to_default(self):
        """辞書でなければ既定矩形"""
        self.assertEqual(normalize_rect(None, 0), default_mask_rect(0))
        self.assertEqual(normalize_rect("0.5", 1), default_mask_rect(1))
        self.assertEqual(normalize_rect([0.5, 0.5], 2), default_mask_rect(2))

    def test_non_numeric_falls_back_to_default(self):
        """数値でない値が混ざれば既定矩形"""
        rect = normalize_rect({"x": "abc", "y": 0.2, "w": 0.3, "h": 0.4}, 3)
        self.assertEqual(rect, default_mask_rect(3))

    def test_missing_key_falls_back_to_default(self):
        """キーが足りなければ既定矩形"""
        rect = normalize_rect({"x": 0.1, "y": 0.2, "w": 0.3}, 4)
        self.assertEqual(rect, default_mask_rect(4))

    def test_size_clamped_to_min(self):
        """最小サイズ未満は最小サイズまで広げる"""
        rect = normalize_rect({"x": 0.1, "y": 0.1, "w": 0.0, "h": -5}, 0)
        self.assertEqual(rect["w"], MIN_MASK_SIZE)
        self.assertEqual(rect["h"], MIN_MASK_SIZE)

    def test_size_clamped_to_max(self):
        """幅・高さは 1.0 を超えない"""
        rect = normalize_rect({"x": 0.5, "y": 0.5, "w": 3.0, "h": 2.0}, 0)
        self.assertEqual(rect, {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0})

    def test_position_clamped_to_range(self):
        """位置は 0.0〜1.0 に収める"""
        rect = normalize_rect({"x": -1.0, "y": 5.0, "w": 0.2, "h": 0.2}, 0)
        self.assertEqual(rect["x"], 0.0)
        self.assertAlmostEqual(rect["y"], 0.8)

    def test_overflow_pushes_position_back(self):
        """はみ出しは位置を押し戻して吸収し、サイズは縮めない"""
        rect = normalize_rect({"x": 0.9, "y": 0.9, "w": 0.3, "h": 0.4}, 0)
        self.assertAlmostEqual(rect["x"], 0.7)
        self.assertAlmostEqual(rect["y"], 0.6)
        self.assertEqual(rect["w"], 0.3)
        self.assertEqual(rect["h"], 0.4)


class TestParseMasks(unittest.TestCase):
    def test_broken_json_fills_defaults(self):
        """壊れた JSON は全件を既定矩形で埋める"""
        rects = parse_masks("{{{", 3)
        self.assertEqual(rects, [default_mask_rect(i) for i in range(3)])

    def test_not_array_fills_defaults(self):
        """配列でなければ全件を既定矩形で埋める"""
        rects = parse_masks('{"x": 0.1}', 2)
        self.assertEqual(rects, [default_mask_rect(i) for i in range(2)])

    def test_empty_array_fills_defaults(self):
        """空配列は全件を既定矩形で埋める"""
        rects = parse_masks("[]", 2)
        self.assertEqual(rects, [default_mask_rect(i) for i in range(2)])

    def test_shortage_is_filled(self):
        """要素が足りない分だけ既定矩形で補う"""
        given = {"x": 0.1, "y": 0.1, "w": 0.2, "h": 0.2}
        rects = parse_masks(json.dumps([given]), 3)
        self.assertEqual(rects[0], given)
        self.assertEqual(rects[1], default_mask_rect(1))
        self.assertEqual(rects[2], default_mask_rect(2))

    def test_surplus_is_truncated(self):
        """要素が多ければ先頭 count 件だけ使う"""
        source = [{"x": i / 10, "y": 0.1, "w": 0.2, "h": 0.2} for i in range(5)]
        rects = parse_masks(json.dumps(source), 2)
        self.assertEqual(len(rects), 2)
        self.assertEqual(rects[0], source[0])
        self.assertEqual(rects[1], source[1])

    def test_zero_count_returns_empty(self):
        """count が 0 なら空リスト"""
        self.assertEqual(parse_masks("[]", 0), [])


class TestRectToPixels(unittest.TestCase):
    def test_full_range(self):
        """全面の矩形は 0 から端まで"""
        pixels = rect_to_pixels({"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}, 1024, 512)
        self.assertEqual(pixels, (0, 0, 1024, 512))

    def test_rounding(self):
        """相対値は四捨五入でピクセルにする"""
        pixels = rect_to_pixels({"x": 0.25, "y": 0.5, "w": 0.5, "h": 0.25}, 100, 100)
        self.assertEqual(pixels, (25, 50, 75, 75))

    def test_clamped_to_size(self):
        """範囲外は座標系のサイズでクランプする"""
        pixels = rect_to_pixels({"x": 0.9, "y": 0.9, "w": 0.5, "h": 0.5}, 100, 100)
        self.assertEqual(pixels, (90, 90, 100, 100))

    def test_minimum_one_pixel(self):
        """丸めで潰れても最低1ピクセルを確保する"""
        pixels = rect_to_pixels({"x": 0.5, "y": 0.5, "w": 0.001, "h": 0.001}, 100, 100)
        self.assertEqual(pixels, (50, 50, 51, 51))

    def test_minimum_one_pixel_at_edge(self):
        """右端・下端で潰れても座標系の外へ出さない"""
        pixels = rect_to_pixels({"x": 1.0, "y": 1.0, "w": 0.001, "h": 0.001}, 100, 100)
        self.assertEqual(pixels, (99, 99, 100, 100))


if __name__ == "__main__":
    unittest.main()
