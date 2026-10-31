import sys
import os
import unittest

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.nai_prompt_util import convert_to_nai, convert_to_sd


class TestSdToNaiNumber(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(convert_to_nai("(aaa:1.2)"), "1.2::aaa ::")

    def test_space_before_close(self):
        self.assertEqual(convert_to_nai("(aaa5:1.2),(bbb:1.3)"), "1.2::aaa5 ::,1.3::bbb ::")

    def test_negative(self):
        self.assertEqual(convert_to_nai("(aaa:-2)"), "-2::aaa ::")

    def test_keep_newline(self):
        self.assertEqual(convert_to_nai("(aaa:1.2),\n(bbb:0.8)"), "1.2::aaa ::,\n0.8::bbb ::")


class TestSdToNaiBrace(unittest.TestCase):
    def test_up(self):
        self.assertEqual(convert_to_nai("(aaa:1.1)", "brace"), "{{aaa}}")

    def test_down(self):
        self.assertEqual(convert_to_nai("(aaa:0.9)", "brace"), "[[aaa]]")

    def test_zero_or_negative_fallback_number(self):
        self.assertEqual(convert_to_nai("(aaa:-2)", "brace"), "-2::aaa ::")
        self.assertEqual(convert_to_nai("(aaa:0)", "brace"), "0::aaa ::")


class TestNaiToSdNumber(unittest.TestCase):
    def test_negative_keep(self):
        self.assertEqual(convert_to_sd("-2::aaa::", remove_negative=False), "(aaa:-2)")

    def test_remove_negative(self):
        self.assertEqual(
            convert_to_sd("1.4::1girl::, -1.5::black hair::, 1.2::blonde hair,"),
            "(1girl:1.4), , (blonde hair:1.2),",
        )

    def test_unclosed(self):
        self.assertEqual(
            convert_to_sd("1.2::blonde hair, 1.3::from side::"),
            "(blonde hair:1.2), (from side:1.3)",
        )

    def test_multi_tags(self):
        self.assertEqual(convert_to_sd("1.2::aaaa, bbbb::"), "(aaaa, bbbb:1.2)")

    def test_unclosed_multi(self):
        self.assertEqual(convert_to_sd("1.2::aaaa, 2::bbbb::"), "(aaaa:1.2), (bbbb:2)")

    def test_zero(self):
        self.assertEqual(convert_to_sd("0::aaa::"), "(aaa:0)")

    def test_space_before_close(self):
        self.assertEqual(convert_to_sd("1.2::aaa5 ::"), "(aaa5:1.2)")

    def test_round_trip(self):
        sd = "(aaa5:1.2),(bbb:1.3)"
        self.assertEqual(convert_to_sd(convert_to_nai(sd)), sd)

    def test_stop_at_newline(self):
        self.assertEqual(convert_to_sd("1.2::aaa\nbbb"), "(aaa:1.2)\nbbb")

    def test_word_digit_not_weight(self):
        self.assertEqual(convert_to_sd("2girls::"), "2girls::")

    def test_weight_format(self):
        self.assertEqual(convert_to_sd("1.40::aaa::, .5::bbb::"), "(aaa:1.4), (bbb:0.5)")

    def test_empty(self):
        self.assertEqual(convert_to_sd(""), "")


class TestNaiToSdBrace(unittest.TestCase):
    def test_up(self):
        self.assertEqual(convert_to_sd("{{aaa}}", "brace"), "(aaa:1.1)")

    def test_down(self):
        self.assertEqual(convert_to_sd("[[aaa]], bbb", "brace"), "(aaa:0.9), bbb")


if __name__ == "__main__":
    unittest.main()
