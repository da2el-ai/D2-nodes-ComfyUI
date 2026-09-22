import sys
import os
import random
import unittest

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.random_util import (
    MODE_ABSOLUTE,
    MODE_RELATIVE,
    NUMBER_TYPE_FLOAT,
    NUMBER_TYPE_INT,
    random_relative,
    random_rect,
    random_size,
    sort_range,
    to_point_value,
)


class TestSortRange(unittest.TestCase):
    def test_keeps_order(self):
        """正しい順序ならそのまま返す"""
        self.assertEqual(sort_range(100, 500), (100, 500))

    def test_swaps_reversed(self):
        """逆転していたら入れ替える"""
        self.assertEqual(sort_range(800, 200), (200, 800))

    def test_same_value(self):
        """同値ならそのまま"""
        self.assertEqual(sort_range(512, 512), (512, 512))


class TestRandomRelative(unittest.TestCase):
    def test_within_range(self):
        """指定範囲の内側に収まる"""
        rng = random.Random(0)
        for _ in range(1000):
            value = random_relative(rng, 0.2, 0.8)
            self.assertGreaterEqual(value, 0.2)
            self.assertLessEqual(value, 0.8)

    def test_reversed_range(self):
        """min / max が逆転していても同じ範囲になる"""
        rng = random.Random(0)
        for _ in range(100):
            value = random_relative(rng, 0.8, 0.2)
            self.assertGreaterEqual(value, 0.2)
            self.assertLessEqual(value, 0.8)

    def test_clamps_out_of_bounds(self):
        """0.0〜1.0 の外を指定してもクランプされる"""
        rng = random.Random(0)
        for _ in range(100):
            value = random_relative(rng, -5.0, 9.0)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_same_min_max_is_fixed(self):
        """min == max ならその値で固定される"""
        rng = random.Random(0)
        self.assertAlmostEqual(random_relative(rng, 0.3, 0.3), 0.3)


class TestRandomSize(unittest.TestCase):
    def test_within_range(self):
        """指定範囲の内側に収まる"""
        rng = random.Random(0)
        for _ in range(1000):
            value = random_size(rng, 100, 300, 1024)
            self.assertGreaterEqual(value, 100)
            self.assertLessEqual(value, 300)

    def test_includes_both_ends(self):
        """両端の値も出る（randint なので閉区間）"""
        rng = random.Random(0)
        values = {random_size(rng, 1, 3, 1024) for _ in range(200)}
        self.assertEqual(values, {1, 2, 3})

    def test_clamps_to_limit(self):
        """limit を超える指定は limit に抑えられる"""
        rng = random.Random(0)
        for _ in range(100):
            value = random_size(rng, 100, 99999, 512)
            self.assertLessEqual(value, 512)

    def test_min_over_limit(self):
        """min まで limit を超えていたら limit で固定される"""
        rng = random.Random(0)
        self.assertEqual(random_size(rng, 2000, 3000, 512), 512)

    def test_never_zero(self):
        """0 以下を指定しても 1 以上になる"""
        rng = random.Random(0)
        for _ in range(100):
            self.assertGreaterEqual(random_size(rng, 0, 0, 512), 1)


class TestRandomRect(unittest.TestCase):
    def test_always_inside_canvas(self):
        """1000 回試行しても必ず width × height の内側に収まる"""
        rng = random.Random(0)
        for _ in range(1000):
            rect = random_rect(rng, 1024, 768, 64, 900, 64, 900)
            self.assertGreaterEqual(rect["x"], 0)
            self.assertGreaterEqual(rect["y"], 0)
            self.assertLessEqual(rect["x"] + rect["w"], 1024)
            self.assertLessEqual(rect["y"] + rect["h"], 768)

    def test_fits_when_size_equals_canvas(self):
        """矩形がキャンバスと同じ大きさなら座標は 0 になる"""
        rng = random.Random(0)
        rect = random_rect(rng, 512, 512, 512, 512, 512, 512)
        self.assertEqual(rect, {"x": 0, "y": 0, "w": 512, "h": 512})

    def test_reproducible_by_seed(self):
        """同じ seed なら同じ結果になる"""
        first = random_rect(random.Random(123), 1024, 1024, 100, 500, 100, 500)
        second = random_rect(random.Random(123), 1024, 1024, 100, 500, 100, 500)
        self.assertEqual(first, second)

    def test_different_seed_differs(self):
        """seed が違えば結果も変わる（1000 回中すべて同じにはならない）"""
        results = {
            tuple(random_rect(random.Random(seed), 1024, 1024, 100, 500, 100, 500).values())
            for seed in range(1000)
        }
        self.assertGreater(len(results), 1)


class TestToPointValue(unittest.TestCase):
    def test_absolute_int(self):
        """absolute + int は四捨五入した int"""
        value = to_point_value(0.5032, 1024, MODE_ABSOLUTE, NUMBER_TYPE_INT)
        self.assertIsInstance(value, int)
        self.assertEqual(value, 515)

    def test_absolute_float(self):
        """absolute + float は丸めない float"""
        value = to_point_value(0.5032, 1024, MODE_ABSOLUTE, NUMBER_TYPE_FLOAT)
        self.assertIsInstance(value, float)
        self.assertAlmostEqual(value, 515.2768)

    def test_relative_ignores_number_type(self):
        """relative は number_type に関わらず float の相対値"""
        for number_type in (NUMBER_TYPE_INT, NUMBER_TYPE_FLOAT):
            value = to_point_value(0.5032, 1024, MODE_RELATIVE, number_type)
            self.assertIsInstance(value, float)
            self.assertAlmostEqual(value, 0.5032)

    def test_absolute_bounds(self):
        """absolute の値域は 0〜size（両端を含む）"""
        self.assertEqual(to_point_value(0.0, 1024, MODE_ABSOLUTE, NUMBER_TYPE_INT), 0)
        self.assertEqual(to_point_value(1.0, 1024, MODE_ABSOLUTE, NUMBER_TYPE_INT), 1024)


if __name__ == "__main__":
    unittest.main()
