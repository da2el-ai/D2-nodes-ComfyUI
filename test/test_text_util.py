import sys
import os
import unittest

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.text_util import sanitize_prompt


class TestSanitizeV1(unittest.TestCase):
    """v1 挙動のリグレッション（新パラメータは既定値）"""

    def test_underscore_to_space(self):
        self.assertEqual(sanitize_prompt("long_hair, blue_eyes"), "long hair, blue eyes")

    def test_protect_score(self):
        self.assertEqual(sanitize_prompt("score_9, score_8_up"), "score_9, score_8_up")

    def test_protect_lora(self):
        self.assertEqual(
            sanitize_prompt("<lora:my_cool_lora:1.0>, 1girl"),
            "<lora:my_cool_lora:1.0>, 1girl",
        )

    def test_normalize_comma_spaces(self):
        self.assertEqual(sanitize_prompt("a ,  b,c"), "a, b, c")

    def test_remove_extra_comma(self):
        self.assertEqual(sanitize_prompt("a,,b"), "a, b")
        self.assertEqual(sanitize_prompt("a, ,b"), "a, b")

    def test_remove_leading_comma(self):
        self.assertEqual(sanitize_prompt(", a"), "a")

    def test_keep_newline(self):
        # 改行は保持したまま行頭カンマを削除
        self.assertEqual(sanitize_prompt("a\n, b"), "a\nb")

    def test_all_off_passthrough(self):
        # 全処理 off なら（改行正規化以外）そのまま
        self.assertEqual(
            sanitize_prompt(
                "a_b,,c",
                underscore_to_space=False,
                space_after_comma=False,
                remove_extra_comma=False,
                protect_lora=False,
                protect_score=False,
            ),
            "a_b,,c",
        )


class TestNewlineMode(unittest.TestCase):
    def test_add_comma(self):
        # space_after_comma を off にして純粋な付与結果を見る
        self.assertEqual(
            sanitize_prompt("a\nb", newline_mode="add_comma", space_after_comma=False),
            "a,\nb,",
        )

    def test_add_comma_no_duplicate(self):
        # 既に , で終わる行には追加しない
        self.assertEqual(
            sanitize_prompt("a,\nb", newline_mode="add_comma", space_after_comma=False),
            "a,\nb,",
        )

    def test_add_comma_skip_empty_line(self):
        self.assertEqual(
            sanitize_prompt("a\n\nb", newline_mode="add_comma", space_after_comma=False),
            "a,\n\nb,",
        )

    def test_to_comma(self):
        self.assertEqual(sanitize_prompt("a\nb", newline_mode="to_comma"), "a, b")

    def test_to_comma_no_duplicate(self):
        self.assertEqual(sanitize_prompt("a,\nb", newline_mode="to_comma"), "a, b")

    def test_to_space(self):
        self.assertEqual(sanitize_prompt("a\nb", newline_mode="to_space"), "a b")

    def test_remove(self):
        # 日本語テキストの結合（単純削除）
        self.assertEqual(sanitize_prompt("あいう\nえお", newline_mode="remove"), "あいうえお")


class TestRemoveDuplicateTags(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            sanitize_prompt("1girl, smile, 1girl", remove_duplicate_tags=True),
            "1girl, smile",
        )

    def test_underscore_normalized_key(self):
        # long_hair と long hair は同一視され片方削除
        self.assertEqual(
            sanitize_prompt("long_hair, long hair", remove_duplicate_tags=True),
            "long hair",
        )

    def test_newline_boundary_with_to_comma(self):
        self.assertEqual(
            sanitize_prompt(
                "1girl\nsmile\n1girl",
                remove_duplicate_tags=True,
                newline_mode="to_comma",
            ),
            "1girl, smile",
        )

    def test_case_insensitive(self):
        self.assertEqual(
            sanitize_prompt("1girl, 1GIRL", remove_duplicate_tags=True),
            "1girl",
        )

    def test_duplicate_lora(self):
        # 同一 LoRA 指定はプレースホルダを解決して重複判定される
        self.assertEqual(
            sanitize_prompt(
                "<lora:a:1>, 1girl, <lora:a:1>",
                remove_duplicate_tags=True,
            ),
            "<lora:a:1>, 1girl",
        )


class TestStripTrailingComma(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(sanitize_prompt("a, b,", strip_trailing_comma=True), "a, b")

    def test_trailing_space(self):
        self.assertEqual(sanitize_prompt("a, b, ", strip_trailing_comma=True), "a, b")

    def test_with_add_comma(self):
        # add_comma で必ず末尾に付くカンマを消す
        self.assertEqual(
            sanitize_prompt(
                "a\nb",
                newline_mode="to_comma",
                strip_trailing_comma=True,
            ),
            "a, b",
        )

    def test_keep_trailing_newline(self):
        self.assertEqual(sanitize_prompt("a, b,\n", strip_trailing_comma=True), "a, b\n")


class TestMisc(unittest.TestCase):
    def test_crlf_normalized(self):
        self.assertEqual(sanitize_prompt("a\r\nb", newline_mode="to_space"), "a b")

    def test_empty(self):
        self.assertEqual(sanitize_prompt(""), "")
        self.assertEqual(sanitize_prompt("   "), "   ")


if __name__ == "__main__":
    unittest.main()
