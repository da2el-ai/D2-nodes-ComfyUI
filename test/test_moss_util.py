import sys
import os
import json
import unittest

import torch

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.moss_util import (
    mask_to_bbox,
    build_item,
    check_item_sizes,
    split_meta,
    build_summary,
    build_prompt,
)


def make_mask(width, height, x0, y0, x1, y1):
    """左上原点の矩形（右端・下端は含まない）が 1.0 の [1, H, W] マスク"""
    mask = torch.zeros((1, height, width), dtype=torch.float32)
    mask[:, y0:y1, x0:x1] = 1.0
    return mask


class TestMaskToBbox(unittest.TestCase):
    def test_userguide_example(self):
        """USERGUIDE の EXPLORE と同じ配置で同じ bbox になる"""
        mask = make_mask(1024, 1024, 128, 96, 896, 224)
        self.assertEqual(mask_to_bbox(mask), [-416, -384, -288, 384])

    def test_non_square_canvas(self):
        """縦長キャンバスでは x と y で引く値が違う"""
        mask = make_mask(832, 1216, 116, 300, 716, 1180)
        self.assertEqual(mask_to_bbox(mask), [-308, -300, 572, 300])

    def test_empty_mask_is_full_canvas(self):
        """空マスクはキャンバス全体"""
        mask = torch.zeros((1, 1216, 832))
        self.assertEqual(mask_to_bbox(mask), [-608, -416, 608, 416])

    def test_full_mask(self):
        """全面のマスクもキャンバス全体"""
        mask = torch.ones((1, 512, 768))
        self.assertEqual(mask_to_bbox(mask), [-256, -384, 256, 384])

    def test_2d_mask(self):
        """[H, W] のマスクも受け付ける"""
        mask = make_mask(1024, 1024, 128, 96, 896, 224)[0]
        self.assertEqual(mask_to_bbox(mask), [-416, -384, -288, 384])

    def test_uses_first_batch(self):
        """バッチは先頭だけを使う"""
        first = make_mask(1024, 1024, 0, 0, 512, 512)
        second = make_mask(1024, 1024, 512, 512, 1024, 1024)
        mask = torch.cat([first, second], dim=0)
        self.assertEqual(mask_to_bbox(mask), [-512, -512, 0, 0])

    def test_irregular_mask(self):
        """矩形でないマスクは囲む最小の矩形になる"""
        mask = torch.zeros((1, 100, 100))
        mask[0, 10, 20] = 1.0
        mask[0, 59, 79] = 0.5
        self.assertEqual(mask_to_bbox(mask), [-40, -30, 10, 30])

    def test_odd_size_returns_int(self):
        """幅・高さが奇数でも整数で返る"""
        mask = make_mask(101, 99, 0, 0, 101, 99)
        bbox = mask_to_bbox(mask)
        self.assertTrue(all(isinstance(value, int) for value in bbox))


class TestBuildItem(unittest.TestCase):
    def test_object_ignores_text(self):
        """object のときは text を出さない"""
        item = build_item("object", "A blue mountain.", "IGNORED", [0, 0, 1, 1])
        self.assertEqual(item, {"label": "object", "caption": "A blue mountain.", "bbox": [0, 0, 1, 1]})

    def test_key_order(self):
        """キーは label → caption → text → bbox の順"""
        item = build_item("text", "Large title.", "EXPLORE", [0, 0, 1, 1])
        self.assertEqual(list(item.keys()), ["label", "caption", "text", "bbox"])

    def test_empty_caption_is_omitted(self):
        """caption が空白だけならキーを出さない"""
        item = build_item("text", "  \n ", "EXPLORE", [0, 0, 1, 1])
        self.assertNotIn("caption", item)

    def test_caption_is_stripped(self):
        """caption の前後の空白を除く"""
        item = build_item("object", "  A cat.\n", "", [0, 0, 1, 1])
        self.assertEqual(item["caption"], "A cat.")

    def test_escaped_newline(self):
        """\\n の2文字が改行になる"""
        item = build_item("text", "", "STRONGER\\nHAPPIER", [0, 0, 1, 1])
        self.assertEqual(item["text"], "STRONGER\nHAPPIER")

    def test_real_newline_is_kept(self):
        """実際の改行はそのまま残る"""
        item = build_item("text", "", "STRONGER\nHAPPIER", [0, 0, 1, 1])
        self.assertEqual(item["text"], "STRONGER\nHAPPIER")

    def test_empty_text_raises(self):
        """text のときに text が空ならエラー"""
        with self.assertRaises(ValueError):
            build_item("text", "Large title.", "  ", [0, 0, 1, 1])

    def test_object_with_empty_text_is_ok(self):
        """object なら text が空でもエラーにならない"""
        item = build_item("object", "A cat.", "", [0, 0, 1, 1])
        self.assertEqual(item["label"], "object")


class TestCheckItemSizes(unittest.TestCase):
    def test_same_sizes(self):
        """サイズが揃っていれば何もしない"""
        check_item_sizes([(1024, 1024), (1024, 1024)])
        check_item_sizes([])

    def test_different_sizes_raise(self):
        """サイズが違えばエラー"""
        with self.assertRaises(ValueError):
            check_item_sizes([(1024, 1024), (832, 1216)])


class TestSummary(unittest.TestCase):
    def test_split_meta(self):
        """カンマで分割し、空白と空の要素を除く"""
        self.assertEqual(split_meta(" poster, , illustration ,"), ["poster", "illustration"])
        self.assertEqual(split_meta(""), [])

    def test_summary_key_order(self):
        """キーは meta → canvas → caption の順"""
        summary = build_summary("poster", "single", "A poster.")
        self.assertEqual(list(summary.keys()), ["meta", "canvas", "caption"])

    def test_empty_values_are_omitted(self):
        """空の項目はキーを出さない"""
        self.assertEqual(build_summary(" , ", " ", "\n"), {})


class TestBuildPrompt(unittest.TestCase):
    def test_userguide_example(self):
        """USERGUIDE の例と同じ内容の JSON になる"""
        items = [
            build_item("text", "Large dark-blue uppercase title centered at the top.", "EXPLORE", [-416, -384, -288, 384]),
            build_item("object", "A flat blue mountain illustration in the lower center.", "", [-192, -288, 384, 288]),
        ]
        prompt = build_prompt(
            "poster",
            "single",
            "A minimalist travel poster with a cream background, a blue mountain illustration, and the title EXPLORE at the top.",
            items,
        )
        expected = {
            "summary": {
                "meta": ["poster"],
                "canvas": "single",
                "caption": "A minimalist travel poster with a cream background, a blue mountain illustration, and the title EXPLORE at the top.",
            },
            "items": [
                {
                    "label": "text",
                    "caption": "Large dark-blue uppercase title centered at the top.",
                    "text": "EXPLORE",
                    "bbox": [-416, -384, -288, 384],
                },
                {
                    "label": "object",
                    "caption": "A flat blue mountain illustration in the lower center.",
                    "bbox": [-192, -288, 384, 288],
                },
            ],
            "bbox_coord_space": "abs_centralized",
            "bbox_format": "yxyx",
        }
        self.assertEqual(json.loads(prompt), expected)

    def test_top_level_key_order(self):
        """トップレベルのキーは公式サンプルの順"""
        prompt = build_prompt("", "", "", [])
        self.assertEqual(list(json.loads(prompt).keys()), ["summary", "items", "bbox_coord_space", "bbox_format"])

    def test_compact_and_non_ascii(self):
        """空白なしの1行で、日本語はエスケープしない"""
        items = [build_item("text", "", "夏の夢\\n2026", [0, 0, 1, 1])]
        prompt = build_prompt("", "", "", items)
        self.assertNotIn(", ", prompt)
        self.assertNotIn("\n", prompt)
        self.assertIn("夏の夢\\n2026", prompt)

    def test_empty_items(self):
        """アイテムが無くても items は空配列で出る"""
        prompt = build_prompt("", "", "", [])
        self.assertEqual(json.loads(prompt)["items"], [])


if __name__ == "__main__":
    unittest.main()
