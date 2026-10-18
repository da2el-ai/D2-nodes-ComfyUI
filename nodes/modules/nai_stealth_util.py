import gzip
import json
import numpy as np
from PIL import Image


# NovelAI がアルファチャンネルの LSB に埋め込むメタデータ（gzip 圧縮形式）のマジック
STEALTH_MAGIC = b"stealth_pngcomp"
MAGIC_BITS = len(STEALTH_MAGIC) * 8
LENGTH_BITS = 32


"""
アルファチャンネルの LSB を列優先（x=0 の列を上から下 → x=1 の列 …）で並べた bit 列を返す
"""
def _get_alpha_lsb_bits(img: Image.Image) -> np.ndarray:
    alpha = np.array(img.getchannel("A"), dtype=np.uint8)
    return (alpha.T & 1).flatten()


"""
bit 列を MSB から 8bit ずつ詰めてバイト列にする
"""
def _bits_to_bytes(bits: np.ndarray) -> bytes:
    return np.packbits(bits).tobytes()


"""
画像に NovelAI stealth info が埋め込まれているか判定する（先頭のマジックだけを見る）
"""
def has_stealth_info(img: Image.Image) -> bool:
    if "A" not in img.getbands():
        return False

    bits = _get_alpha_lsb_bits(img)
    if len(bits) < MAGIC_BITS + LENGTH_BITS:
        return False

    return _bits_to_bytes(bits[:MAGIC_BITS]) == STEALTH_MAGIC


"""
NovelAI stealth info を復号して dict で返す。埋め込みが無い・壊れている場合は None
"""
def read_stealth_info(img: Image.Image) -> dict | None:
    if not has_stealth_info(img):
        return None

    bits = _get_alpha_lsb_bits(img)
    length_bits = bits[MAGIC_BITS:MAGIC_BITS + LENGTH_BITS]
    payload_len = int.from_bytes(_bits_to_bytes(length_bits), "big")

    start = MAGIC_BITS + LENGTH_BITS
    if payload_len == 0 or start + payload_len > len(bits):
        return None

    try:
        data = gzip.decompress(_bits_to_bytes(bits[start:start + payload_len]))
        info = json.loads(data.decode("utf-8"))
    except Exception:
        return None

    return info if isinstance(info, dict) else None
