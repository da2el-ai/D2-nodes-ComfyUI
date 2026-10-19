"""
MOSS-Image のレイアウトプロンプト（JSON）を組み立てる純粋関数群。
D2 Moss Item / D2 Moss Prompt から使う。
仕様は .claude/specs/d2-moss-prompt.md を参照。
"""
import json

LABEL_OBJECT = "object"
LABEL_TEXT = "text"
LABELS = [LABEL_OBJECT, LABEL_TEXT]

BBOX_COORD_SPACE = "abs_centralized"
BBOX_FORMAT = "yxyx"


"""
マスクから bbox を算出する。
値が 0 より大きい画素を囲む最小の矩形を、キャンバス中心原点の
[y_min, x_min, y_max, x_max]（整数）で返す。右端・下端はピクセルの境界（最後の画素 + 1）。
空マスクはキャンバス全体を囲んでいるものとみなす。
mask は [B, H, W] または [H, W] の torch.Tensor。バッチは先頭だけを使う。
"""
def mask_to_bbox(mask):
    if mask.dim() == 3:
        mask = mask[0]

    height, width = mask.shape
    ys, xs = (mask > 0).nonzero(as_tuple=True)

    if len(ys) == 0:
        y_min, x_min, y_max, x_max = 0, 0, height, width
    else:
        y_min = int(ys.min())
        x_min = int(xs.min())
        y_max = int(ys.max()) + 1
        x_max = int(xs.max()) + 1

    half_w = width / 2
    half_h = height / 2
    return [
        round(y_min - half_h),
        round(x_min - half_w),
        round(y_max - half_h),
        round(x_max - half_w),
    ]


"""
レイアウトのアイテム1件を dict で作る。キーの順番は USERGUIDE の例に合わせる。
caption が空ならキーを出さない。object のときは text を無視する。
text のときは「\\n」の2文字を改行にし、空なら ValueError。
"""
def build_item(label, caption, text, bbox):
    item = {"label": label}

    caption = caption.strip()
    if caption:
        item["caption"] = caption

    if label == LABEL_TEXT:
        # 1行入力の欄では改行を打てないので、\n の2文字を改行の代わりにする
        text = text.replace("\\n", "\n")
        if not text.strip():
            raise ValueError("[D2 Moss Item] label が text のときは text を入力してください")
        item["text"] = text

    item["bbox"] = bbox
    return item


"""
アイテム全部のマスクサイズが揃っているかを確かめる。違えば ValueError。
サイズが違うと座標の原点がアイテムごとにずれ、意味のないレイアウトになる。
sizes は (width, height) のリスト。
"""
def check_item_sizes(sizes):
    if len(set(sizes)) > 1:
        size_list = ", ".join(f"{w}x{h}" for w, h in sizes)
        raise ValueError(f"[D2 Moss Prompt] アイテムのマスクサイズが揃っていません: {size_list}")


"""
カンマ区切りの文字列を配列にする。前後の空白を除き、空の要素は捨てる
"""
def split_meta(meta):
    return [tag.strip() for tag in meta.split(",") if tag.strip()]


"""
summary の dict を作る。空の項目はキーを出さない
"""
def build_summary(meta, canvas_type, summary_caption):
    summary = {}

    meta_list = split_meta(meta)
    if meta_list:
        summary["meta"] = meta_list

    canvas_type = canvas_type.strip()
    if canvas_type:
        summary["canvas"] = canvas_type

    summary_caption = summary_caption.strip()
    if summary_caption:
        summary["caption"] = summary_caption

    return summary


"""
レイアウトプロンプトの JSON 文字列を作る。
キーの順番は公式サンプルに合わせ、空白なしの1行・非 ASCII はそのまま出力する。
"""
def build_prompt(meta, canvas_type, summary_caption, items):
    prompt = {
        "summary": build_summary(meta, canvas_type, summary_caption),
        "items": items,
        "bbox_coord_space": BBOX_COORD_SPACE,
        "bbox_format": BBOX_FORMAT,
    }
    return json.dumps(prompt, ensure_ascii=False, separators=(",", ":"))
