import sys
import os
import gzip
import json
import unittest
import numpy as np
from PIL import Image

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.nai_stealth_util import has_stealth_info, read_stealth_info, STEALTH_MAGIC

SAMPLE_INFO = {
    "Software": "NovelAI",
    "Comment": json.dumps({"prompt": "1girl, solo", "uc": "lowres"}),
}


def _make_stealth_image(payload_bytes, magic=STEALTH_MAGIC, length=None, size=(64, 64), mode="RGBA"):
    """アルファ LSB に stealth info を列優先で書き込んだ画像を作る"""
    if length is None:
        length = len(payload_bytes) * 8
    data = magic + length.to_bytes(4, "big") + payload_bytes
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

    w, h = size
    alpha = np.full(w * h, 255, dtype=np.uint8)
    alpha[:len(bits)] = 254 | bits
    alpha = alpha.reshape(w, h).T

    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    img = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    return img.convert(mode) if mode != "RGBA" else img


def _gzip_json(info):
    return gzip.compress(json.dumps(info).encode("utf-8"))


class TestNaiStealth(unittest.TestCase):
    def test_read_valid(self):
        """埋め込みありの画像を判定・復号できる"""
        img = _make_stealth_image(_gzip_json(SAMPLE_INFO))
        self.assertTrue(has_stealth_info(img))
        self.assertEqual(read_stealth_info(img), SAMPLE_INFO)

    def test_magic_mismatch(self):
        """マジック不一致なら検出しない"""
        img = _make_stealth_image(_gzip_json(SAMPLE_INFO), magic=b"stealth_pnginfo")
        self.assertFalse(has_stealth_info(img))
        self.assertIsNone(read_stealth_info(img))

    def test_opaque_image(self):
        """全面不透明の通常画像は検出しない"""
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 255))
        self.assertFalse(has_stealth_info(img))

    def test_no_alpha(self):
        """アルファなしの画像は検出しない"""
        img = _make_stealth_image(_gzip_json(SAMPLE_INFO), mode="RGB")
        self.assertFalse(has_stealth_info(img))
        self.assertIsNone(read_stealth_info(img))

    def test_too_small(self):
        """マジック + 長さに満たない小さな画像は検出しない"""
        img = Image.new("RGBA", (4, 4), (0, 0, 0, 255))
        self.assertFalse(has_stealth_info(img))

    def test_length_overflow(self):
        """長さが画像の容量を超える場合は None（判定は True）"""
        img = _make_stealth_image(_gzip_json(SAMPLE_INFO), length=64 * 64 * 2)
        self.assertTrue(has_stealth_info(img))
        self.assertIsNone(read_stealth_info(img))

    def test_broken_gzip(self):
        """gzip が壊れている場合は None（判定は True）"""
        img = _make_stealth_image(b"not gzip data")
        self.assertTrue(has_stealth_info(img))
        self.assertIsNone(read_stealth_info(img))


if __name__ == "__main__":
    unittest.main()
