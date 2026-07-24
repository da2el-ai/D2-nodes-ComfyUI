import sys
import os
import unittest

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.csv_util import parse_range, slice_range, load_csv


class TestParseRange(unittest.TestCase):
    def test_empty_is_all(self):
        self.assertIsNone(parse_range(""))
        self.assertIsNone(parse_range("   "))

    def test_single(self):
        self.assertEqual(parse_range("3"), (3, 3))

    def test_open_end(self):
        self.assertEqual(parse_range("2-"), (2, None))

    def test_open_start(self):
        self.assertEqual(parse_range("-4"), (1, 4))

    def test_both(self):
        self.assertEqual(parse_range("2-4"), (2, 4))

    def test_start_gt_end_allowed(self):
        # 開始>終了はパースは通り、スライスで空になる
        self.assertEqual(parse_range("4-2"), (4, 2))

    def test_malformed_raises(self):
        for bad in ["2--4", "a-3", "0", "-", "abc", "1-2-3", "0-4", "-0"]:
            with self.assertRaises(ValueError, msg=bad):
                parse_range(bad)

    def test_error_message_axis(self):
        with self.assertRaises(ValueError) as cm:
            parse_range("x", axis="column")
        self.assertIn("column_index", str(cm.exception))


class TestSliceRange(unittest.TestCase):
    def setUp(self):
        self.seq = ["a", "b", "c", "d", "e"]

    def test_all(self):
        self.assertEqual(slice_range(self.seq, None), self.seq)

    def test_single(self):
        self.assertEqual(slice_range(self.seq, (3, 3)), ["c"])

    def test_open_end(self):
        self.assertEqual(slice_range(self.seq, (2, None)), ["b", "c", "d", "e"])

    def test_open_start(self):
        self.assertEqual(slice_range(self.seq, (1, 4)), ["a", "b", "c", "d"])

    def test_range(self):
        self.assertEqual(slice_range(self.seq, (2, 4)), ["b", "c", "d"])

    def test_out_of_range_empty(self):
        self.assertEqual(slice_range(self.seq, (9, 10)), [])

    def test_start_gt_end_empty(self):
        self.assertEqual(slice_range(self.seq, (4, 2)), [])


class TestLoadCsv(unittest.TestCase):
    CSV = "a1,a2,a3\nb1,b2,b3\nc1,c2,c3"

    def test_list_all(self):
        out, n = load_csv(self.CSV, output_mode="list")
        self.assertEqual(out, [["a1", "a2", "a3"], ["b1", "b2", "b3"], ["c1", "c2", "c3"]])
        self.assertEqual(n, 3)

    def test_row_range(self):
        out, n = load_csv(self.CSV, output_mode="list", row_index="2-3")
        self.assertEqual(out, [["b1", "b2", "b3"], ["c1", "c2", "c3"]])
        self.assertEqual(n, 2)

    def test_column_range(self):
        out, n = load_csv(self.CSV, output_mode="list", column_index="1-2")
        self.assertEqual(out, [["a1", "a2"], ["b1", "b2"], ["c1", "c2"]])
        self.assertEqual(n, 3)

    def test_single_cell(self):
        out, n = load_csv(self.CSV, output_mode="list", row_index="2", column_index="3")
        self.assertEqual(out, [["b3"]])
        self.assertEqual(n, 1)

    def test_quoted_input_parsed(self):
        # カンマを含むクォート済みセルは1セルに分解される
        out, _ = load_csv('"AAA,BBB",CCC', output_mode="list")
        self.assertEqual(out, [["AAA,BBB", "CCC"]])

    def test_csv_output_doublequote_all(self):
        out, _ = load_csv("AAA,BBB;more", output_mode="csv", use_doublequote=True)
        # 全セルがクォートされる（; はそのまま）
        self.assertEqual(out, '"AAA","BBB;more"')

    def test_csv_output_doublequote_escapes_quote(self):
        out, _ = load_csv('a"b,c', output_mode="csv", use_doublequote=True)
        self.assertEqual(out, '"a""b","c"')

    def test_csv_output_no_doublequote_flattens(self):
        # クォート済み入力を no-doublequote 出力すると区切りが失われる
        out, _ = load_csv('"AAA,BBB","XXX,YYY"', output_mode="csv", use_doublequote=False)
        self.assertEqual(out, "AAA,BBB,XXX,YYY")

    def test_csv_output_multiple_rows(self):
        out, _ = load_csv("a,b\nc,d", output_mode="csv", use_doublequote=False)
        self.assertEqual(out, "a,b\nc,d")

    def test_tsv_input(self):
        out, n = load_csv("a\tb\tc\nd\te\tf", file_type="tsv", output_mode="list")
        self.assertEqual(out, [["a", "b", "c"], ["d", "e", "f"]])
        self.assertEqual(n, 2)

    def test_tsv_to_csv_output(self):
        # TSV を読んで csv 出力するとタブ→カンマになる
        out, _ = load_csv("a\tb\nc\td", file_type="tsv", output_mode="csv", use_doublequote=False)
        self.assertEqual(out, "a,b\nc,d")

    def test_ragged_rows(self):
        # 列数が不揃いでも各行そのまま。列範囲は行ごとに適用
        out, _ = load_csv("a,b,c\nx,y", output_mode="list", column_index="2-3")
        self.assertEqual(out, [["b", "c"], ["y"]])

    def test_empty_text_list(self):
        out, n = load_csv("", output_mode="list")
        self.assertEqual(out, [])
        self.assertEqual(n, 0)

    def test_empty_text_csv(self):
        out, n = load_csv("", output_mode="csv")
        self.assertEqual(out, "")
        self.assertEqual(n, 0)

    def test_out_of_range_row(self):
        out, n = load_csv(self.CSV, output_mode="list", row_index="9-10")
        self.assertEqual(out, [])
        self.assertEqual(n, 0)

    def test_malformed_row_index_raises(self):
        with self.assertRaises(ValueError):
            load_csv(self.CSV, row_index="2--4")

    def test_malformed_column_index_raises(self):
        with self.assertRaises(ValueError):
            load_csv(self.CSV, column_index="a")


if __name__ == "__main__":
    unittest.main()
