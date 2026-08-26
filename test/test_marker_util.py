import sys
import os
import unittest

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.marker_util import (
    MODE_ABSOLUTE,
    MODE_RELATIVE,
    default_marker_position,
    parse_markers,
    to_output_value,
    markers_to_outputs,
)


class TestDefaultMarkerPosition(unittest.TestCase):
    def test_single_is_centered(self):
        self.assertEqual(default_marker_position(0, 1), {"x": 0.5, "y": 0.5})

    def test_evenly_spaced(self):
        positions = [default_marker_position(i, 3)["x"] for i in range(3)]
        self.assertEqual(positions, [0.25, 0.5, 0.75])

    def test_always_vertical_center(self):
        for i in range(5):
            self.assertEqual(default_marker_position(i, 5)["y"], 0.5)

    def test_stays_inside_canvas(self):
        # 端に張り付くと掴みにくいので 0 と 1 は含まない
        for count in range(1, 17):
            for i in range(count):
                x = default_marker_position(i, count)["x"]
                self.assertGreater(x, 0.0)
                self.assertLess(x, 1.0)


class TestParseMarkers(unittest.TestCase):
    def test_normal(self):
        result = parse_markers('[{"x": 0.2, "y": 0.8}]', 1)
        self.assertEqual(result, [{"x": 0.2, "y": 0.8}])

    def test_broken_json_falls_back_to_defaults(self):
        for bad in ['[{"x": 0.2,', "not json", "", "{{{"]:
            self.assertEqual(parse_markers(bad, 2), [
                default_marker_position(0, 2),
                default_marker_position(1, 2),
            ], msg=bad)

    def test_non_list_falls_back_to_defaults(self):
        for bad in ['{"x": 0.2, "y": 0.8}', "42", '"text"', "null"]:
            self.assertEqual(parse_markers(bad, 1), [default_marker_position(0, 1)], msg=bad)

    def test_none_falls_back_to_defaults(self):
        self.assertEqual(parse_markers(None, 1), [default_marker_position(0, 1)])

    def test_empty_array_falls_back_to_defaults(self):
        self.assertEqual(parse_markers("[]", 2), [
            default_marker_position(0, 2),
            default_marker_position(1, 2),
        ])

    def test_shortage_is_filled_with_defaults(self):
        result = parse_markers('[{"x": 0.1, "y": 0.1}]', 3)
        self.assertEqual(result[0], {"x": 0.1, "y": 0.1})
        self.assertEqual(result[1], default_marker_position(1, 3))
        self.assertEqual(result[2], default_marker_position(2, 3))

    def test_surplus_is_truncated(self):
        markers = '[{"x": 0.1, "y": 0.1}, {"x": 0.2, "y": 0.2}, {"x": 0.3, "y": 0.3}]'
        result = parse_markers(markers, 2)
        self.assertEqual(result, [{"x": 0.1, "y": 0.1}, {"x": 0.2, "y": 0.2}])

    def test_out_of_range_is_clamped(self):
        result = parse_markers('[{"x": -0.5, "y": 1.7}]', 1)
        self.assertEqual(result, [{"x": 0.0, "y": 1.0}])

    def test_malformed_element_falls_back_to_default(self):
        # 要素が dict でない / キーが欠けている / 数値でない
        markers = '[3, {"x": 0.5}, {"x": "a", "y": 0.5}]'
        result = parse_markers(markers, 3)
        self.assertEqual(result, [
            default_marker_position(0, 3),
            default_marker_position(1, 3),
            default_marker_position(2, 3),
        ])

    def test_int_values_become_float(self):
        result = parse_markers('[{"x": 0, "y": 1}]', 1)
        self.assertEqual(result, [{"x": 0.0, "y": 1.0}])

    def test_extra_keys_are_ignored(self):
        result = parse_markers('[{"x": 0.4, "y": 0.6, "label": "A"}]', 1)
        self.assertEqual(result, [{"x": 0.4, "y": 0.6}])

    def test_count_matches_requested(self):
        for count in [1, 5, 16]:
            self.assertEqual(len(parse_markers("[]", count)), count)


class TestToOutputValue(unittest.TestCase):
    def test_absolute_converts_to_int(self):
        value = to_output_value(0.25, 1024, MODE_ABSOLUTE)
        self.assertEqual(value, 256)
        self.assertIsInstance(value, int)

    def test_absolute_bounds(self):
        self.assertEqual(to_output_value(0.0, 512, MODE_ABSOLUTE), 0)
        self.assertEqual(to_output_value(1.0, 512, MODE_ABSOLUTE), 512)

    def test_absolute_rounds(self):
        self.assertEqual(to_output_value(0.333, 100, MODE_ABSOLUTE), 33)
        self.assertEqual(to_output_value(0.336, 100, MODE_ABSOLUTE), 34)

    def test_relative_keeps_value(self):
        value = to_output_value(0.25, 1024, MODE_RELATIVE)
        self.assertEqual(value, 0.25)
        self.assertIsInstance(value, float)

    def test_relative_ignores_size(self):
        self.assertEqual(to_output_value(0.7, 64, MODE_RELATIVE),
                         to_output_value(0.7, 4096, MODE_RELATIVE))


class TestMarkersToOutputs(unittest.TestCase):
    def test_flattens_in_xy_order(self):
        markers = [{"x": 0.0, "y": 0.5}, {"x": 1.0, "y": 0.25}]
        result = markers_to_outputs(markers, 800, 600, MODE_ABSOLUTE)
        self.assertEqual(result, [0, 300, 800, 150])

    def test_uses_width_for_x_and_height_for_y(self):
        markers = [{"x": 0.5, "y": 0.5}]
        result = markers_to_outputs(markers, 1000, 200, MODE_ABSOLUTE)
        self.assertEqual(result, [500, 100])

    def test_relative_mode(self):
        markers = [{"x": 0.2, "y": 0.8}]
        self.assertEqual(markers_to_outputs(markers, 1024, 512, MODE_RELATIVE), [0.2, 0.8])

    def test_empty(self):
        self.assertEqual(markers_to_outputs([], 1024, 1024, MODE_ABSOLUTE), [])


if __name__ == "__main__":
    unittest.main()
