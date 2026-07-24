import sys
import os
import unittest
import tempfile

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.caption_util import (
    load_text_file,
    parse_exclude_tags,
    format_caption,
    save_caption,
    count_tags,
    build_tag_report,
    format_tag_report,
)


class TestLoadTextFile(unittest.TestCase):
    def test_missing_file_returns_empty(self):
        """存在しないファイルは空文字を返す"""
        self.assertEqual(load_text_file("z:/no/such/file.txt"), "")
        self.assertEqual(load_text_file(""), "")

    def test_read_raw(self):
        """strip せず生のまま返す"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("1girl, black hair\n")
            self.assertEqual(load_text_file(path), "1girl, black hair\n")


class TestParseExcludeTags(unittest.TestCase):
    def test_comma_and_newline(self):
        """カンマ・改行の両方で区切る"""
        text = "tag1, tag2\ntag3"
        self.assertEqual(parse_exclude_tags(text), ["tag1", "tag2", "tag3"])

    def test_regex_line_kept_whole(self):
        """regex/pattern/ 行はカンマ分割しない"""
        text = "regex/a{2,3}/\ntag1"
        self.assertEqual(parse_exclude_tags(text), ["regex/a{2,3}/", "tag1"])


class TestFormatCaption(unittest.TestCase):
    def test_basic_trim_and_join(self):
        """分割・trim・カンマ空白区切りで結合（区切り統一なし）"""
        result = format_caption(" 1girl ,black hair,  ,smile", word_separator="none")
        self.assertEqual(result, "1girl, black hair, smile")

    def test_word_separator_space(self):
        """word_separator=space は `_` を空白に統一"""
        result = format_caption("black_hair, school_uniform", word_separator="space")
        self.assertEqual(result, "black hair, school uniform")

    def test_word_separator_underscore(self):
        """word_separator=underscore（デフォルト）は空白を `_` に統一"""
        result = format_caption("blue eyes, blue_hair")
        self.assertEqual(result, "blue_eyes, blue_hair")

    def test_word_separator_none(self):
        """word_separator=none は変換しない"""
        result = format_caption("blue eyes, blue_hair", word_separator="none")
        self.assertEqual(result, "blue eyes, blue_hair")

    def test_exclude_exact(self):
        """完全一致で除去"""
        result = format_caption("1girl, black hair, smile", exclude_tags="black hair")
        self.assertEqual(result, "1girl, smile")

    def test_exclude_ignore_case(self):
        """ignore_case=True は大小無視で除去"""
        result = format_caption("1girl, Black Hair", exclude_tags="black hair", ignore_case=True)
        self.assertEqual(result, "1girl")

    def test_exclude_case_sensitive(self):
        """ignore_case=False は大小区別"""
        result = format_caption("1girl, Black Hair", exclude_tags="black hair", ignore_case=False, word_separator="none")
        self.assertEqual(result, "1girl, Black Hair")

    def test_exclude_regex(self):
        """regex/pattern/ にマッチしたタグを除去"""
        result = format_caption("1girl, black hair, blonde hair, smile", exclude_tags="regex/.*hair/")
        self.assertEqual(result, "1girl, smile")

    def test_exclude_word_separator_normalized(self):
        """word_separator=space なら exclude 側の `_` も揃えて比較する"""
        result = format_caption("black_hair, smile", exclude_tags="black_hair", word_separator="space")
        self.assertEqual(result, "smile")

    def test_exclude_escaped_bracket(self):
        """エスケープ括弧 \\( \\) と素の ( ) を同一視して除去（丸括弧）"""
        result = format_caption(r"rem_\(re:zero\), smile", exclude_tags="rem_(re:zero)")
        self.assertEqual(result, "smile")

    def test_exclude_escaped_bracket_reverse(self):
        """text 側が素の括弧・exclude 側がエスケープでも除去できる"""
        result = format_caption("rem_(re:zero), smile", exclude_tags=r"rem_\(re:zero\)")
        self.assertEqual(result, "smile")

    def test_exclude_escaped_square_bracket(self):
        """角括弧 \\[ \\] も同一視"""
        result = format_caption(r"foo_\[bar\], smile", exclude_tags="foo_[bar]")
        self.assertEqual(result, "smile")

    def test_exclude_escaped_bracket_with_word_separator(self):
        """word_separator=space と併用しても括弧同一視が効く"""
        result = format_caption(r"rem_\(re:zero\), smile", exclude_tags="rem (re:zero)", word_separator="space")
        self.assertEqual(result, "smile")

    def test_remove_escape_output(self):
        """remove_escape=True で出力タグの括弧エスケープを外す"""
        result = format_caption(r"rem_\(re:zero\), foo_\[bar\]", remove_escape=True)
        self.assertEqual(result, "rem_(re:zero), foo_[bar]")

    def test_remove_escape_default_keeps(self):
        """デフォルト（remove_escape=False）はエスケープを保持"""
        result = format_caption(r"rem_\(re:zero\)")
        self.assertEqual(result, r"rem_\(re:zero\)")

    def test_invalid_regex_skipped(self):
        """不正な正規表現はスキップ（エラーにしない）"""
        result = format_caption("1girl, smile", exclude_tags="regex/*_hair/")
        self.assertEqual(result, "1girl, smile")

    def test_dedup_keeps_first(self):
        """重複は先勝ちで除去"""
        result = format_caption("1girl, smile, 1girl")
        self.assertEqual(result, "1girl, smile")

    def test_prepend(self):
        """prepend_tags を先頭に追加。既存タグは追加しない"""
        result = format_caption("1girl, smile", prepend_tags="masterpiece, smile")
        self.assertEqual(result, "masterpiece, 1girl, smile")

    def test_trailing_comma(self):
        """末尾カンマ"""
        result = format_caption("1girl", trailing_comma=True)
        self.assertEqual(result, "1girl,")

    def test_empty_text(self):
        """空入力は空出力（trailing_comma も付かない）"""
        result = format_caption("", trailing_comma=True)
        self.assertEqual(result, "")

    def test_process_order(self):
        """区切り統一 → exclude → 重複除去 → prepend の順で処理される"""
        result = format_caption(
            "black_hair, black hair, 1girl",
            exclude_tags="1girl",
            prepend_tags="1girl, masterpiece",
            word_separator="space",
        )
        # black_hair は black hair になり重複除去、1girl は除去、prepend の 1girl は追加される
        self.assertEqual(result, "1girl, masterpiece, black hair")


class TestSaveCaption(unittest.TestCase):
    def test_save_with_extension_replace(self):
        """拡張子を置換したパスに保存する"""
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.join(tmp, "img.jpg")
            save_path = save_caption(base, "1girl", "txt", backup=False)
            self.assertEqual(save_path, os.path.join(tmp, "img.txt"))
            with open(save_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "1girl")

    def test_backup(self):
        """既存ファイルは .bak に退避される（.bak 既存なら上書き）"""
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.join(tmp, "img.jpg")
            txt_path = os.path.join(tmp, "img.txt")
            bak_path = txt_path + ".bak"

            save_caption(base, "old", "txt", backup=True)
            save_caption(base, "new", "txt", backup=True)
            with open(txt_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "new")
            with open(bak_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "old")

            # .bak 既存でもエラーにならず上書きされる
            save_caption(base, "newer", "txt", backup=True)
            with open(bak_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "new")

    def test_no_backup(self):
        """backup=False は .bak を作らない"""
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.join(tmp, "img.jpg")
            save_caption(base, "old", "txt", backup=False)
            save_caption(base, "new", "txt", backup=False)
            self.assertFalse(os.path.isfile(os.path.join(tmp, "img.txt.bak")))

    def test_empty_base_filename_raises(self):
        """base_filename が空なら例外で停止する（カレントに .txt を作らない）"""
        with self.assertRaises(ValueError):
            save_caption("", "1girl", "txt")
        with self.assertRaises(ValueError):
            save_caption("   ", "1girl", "txt")
        self.assertFalse(os.path.isfile(".txt"))

    def test_dry_run_does_not_write(self):
        """dry_run は書き込まず保存予定パスを返す"""
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.join(tmp, "img.jpg")
            save_path = save_caption(base, "1girl", "txt", dry_run=True)
            self.assertEqual(save_path, os.path.join(tmp, "img.txt"))
            self.assertFalse(os.path.isfile(save_path))

    def test_dry_run_no_backup(self):
        """dry_run は既存ファイルを .bak にリネームしない（書き換えない）"""
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.join(tmp, "img.jpg")
            txt_path = os.path.join(tmp, "img.txt")
            save_caption(base, "old", "txt", backup=False)
            save_caption(base, "new", "txt", backup=True, dry_run=True)
            # 既存ファイルは変更されず、.bak も作られない
            with open(txt_path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "old")
            self.assertFalse(os.path.isfile(txt_path + ".bak"))

    def test_dry_run_empty_base_filename_returns_empty(self):
        """dry_run 時は base_filename が空でもエラーにせず空文字を返す"""
        self.assertEqual(save_caption("", "1girl", "txt", dry_run=True), "")


class TestCountTags(unittest.TestCase):
    def _make_files(self, tmp, contents):
        paths = []
        for i, content in enumerate(contents):
            path = os.path.join(tmp, f"{i}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            paths.append(path)
        return paths

    def test_count_desc(self):
        """count_9-0 は出現回数の多い順（同数はタグ名順）"""
        with tempfile.TemporaryDirectory() as tmp:
            files = self._make_files(tmp, ["1girl, smile", "1girl, blush", "1girl"])
            items = count_tags(files, "count_9-0")
            self.assertEqual(items, [("1girl", 3), ("blush", 1), ("smile", 1)])

    def test_count_asc(self):
        """count_0-9 は出現回数の少ない順"""
        with tempfile.TemporaryDirectory() as tmp:
            files = self._make_files(tmp, ["1girl, smile", "1girl"])
            items = count_tags(files, "count_0-9")
            self.assertEqual(items, [("smile", 1), ("1girl", 2)])

    def test_tag_order(self):
        """tag_a-z / tag_z-a はタグ名順"""
        with tempfile.TemporaryDirectory() as tmp:
            files = self._make_files(tmp, ["b, a, c"])
            self.assertEqual(count_tags(files, "tag_a-z"), [("a", 1), ("b", 1), ("c", 1)])
            self.assertEqual(count_tags(files, "tag_z-a"), [("c", 1), ("b", 1), ("a", 1)])

    def test_newline_as_separator(self):
        """キャプション内の改行もタグ区切りとして扱う"""
        with tempfile.TemporaryDirectory() as tmp:
            files = self._make_files(tmp, ["1girl,\nsmile\n"])
            items = count_tags(files, "tag_a-z")
            self.assertEqual(items, [("1girl", 1), ("smile", 1)])

    def test_empty_list(self):
        """対象0件は空リスト"""
        self.assertEqual(count_tags([], "count_9-0"), [])


class TestBuildTagReport(unittest.TestCase):
    def test_with_count(self):
        report = build_tag_report([("1girl", 3), ("smile", 1)])
        self.assertEqual(report, "1girl,3\nsmile,1")

    def test_without_count(self):
        report = build_tag_report([("1girl", 3), ("smile", 1)], without_count=True)
        self.assertEqual(report, "1girl\nsmile")


class TestFormatTagReport(unittest.TestCase):
    EDITED = "1girl,100\n// black hair,90\n# twintails,90\nschool uniform,80"

    def test_remove_comment_newline(self):
        """コメント行を捨てて残りをタグリスト化（デフォルトは改行区切り）"""
        result = format_tag_report(self.EDITED, "remove_comment")
        self.assertEqual(result, "1girl\nschool uniform")

    def test_output_comment_newline(self):
        """コメント行のみをタグリスト化（改行区切り）"""
        result = format_tag_report(self.EDITED, "output_comment")
        self.assertEqual(result, "black hair\ntwintails")

    def test_separator_comma(self):
        """separator=comma（旧表記エイリアス）はカンマ＋空白の1行で結合"""
        result = format_tag_report(self.EDITED, "remove_comment", "comma")
        self.assertEqual(result, "1girl, school uniform")

    def test_separator_literal_string(self):
        """separator に実際の区切り文字列を渡せる（新契約）"""
        result = format_tag_report(self.EDITED, "remove_comment", ", ")
        self.assertEqual(result, "1girl, school uniform")
        result = format_tag_report(self.EDITED, "remove_comment", "\n")
        self.assertEqual(result, "1girl\nschool uniform")

    def test_line_without_count(self):
        """回数の無い行（手書きの regex 行など）もそのまま通す"""
        result = format_tag_report("regex/.*hair/\n1girl,10", "remove_comment")
        self.assertEqual(result, "regex/.*hair/\n1girl")

    def test_regex_with_comma_survives_roundtrip(self):
        """改行区切りなら、カンマを含む正規表現がそのまま exclude エントリとして復元される"""
        report = format_tag_report("regex/a{2,3}/\n1girl,10", "remove_comment")
        entries = parse_exclude_tags(report)
        self.assertEqual(entries, ["regex/a{2,3}/", "1girl"])

    def test_empty(self):
        self.assertEqual(format_tag_report("", "remove_comment"), "")


if __name__ == "__main__":
    unittest.main()
