"""
テキスト整形の純ロジック。
ComfyUI 非依存にして単体テスト（test/test_text_util.py）できるようにする。
"""
import re


# newline_mode の選択肢
NEWLINE_MODES = ["keep", "add_comma", "to_comma", "to_space", "remove"]


def _resolve_placeholders(text, protected):
    """退避したプレースホルダ \\x00n\\x00 を元文字列へ戻す"""
    if not protected:
        return text
    return re.sub(r"\x00(\d+)\x00", lambda m: protected[int(m.group(1))], text)


def _remove_duplicate_tags(text, protected):
    """
    `,` と改行の両方を境界としてタグに分割し、重複タグを削除する（先勝ち）。
    区切り文字の構造は保持し、削除したタグに隣接する区切り1つも消して
    区切りが宙に浮かないようにする（残った ,, は後段 remove_extra_comma が掃除する）。
    比較キー: プレースホルダを元文字列へ解決 → strip → 小文字化 → `_` を半角スペースへ正規化。
    """
    # キャプチャ付き split で区切り文字も残す（偶数index=タグ, 奇数index=区切り）
    parts = re.split(r"([,\n])", text)
    seen = set()

    for i in range(0, len(parts), 2):
        key = _resolve_placeholders(parts[i], protected).strip().lower().replace("_", " ")
        if key == "":
            # 空・空白のみのタグは重複判定しない（構造を保つ）
            continue
        if key in seen:
            parts[i] = ""
            # 隣接する区切りを1つ消す（前を優先、無ければ後ろ）
            if i - 1 >= 0:
                parts[i - 1] = ""
            elif i + 1 < len(parts):
                parts[i + 1] = ""
        else:
            seen.add(key)

    return "".join(parts)


def _apply_newline_mode(text, mode):
    """改行の変換"""
    if mode == "add_comma":
        # 各行末に `,` を追加。改行は保持。空行・既に `,` で終わる行（行末の空白/タブは無視）は追加しない
        new_lines = []
        for line in text.split("\n"):
            stripped = line.rstrip(" \t")
            if stripped == "" or stripped.endswith(","):
                new_lines.append(line)
            else:
                new_lines.append(line + ",")
        return "\n".join(new_lines)

    if mode == "to_comma":
        # 改行を `,` に変換して1行化。既に `,`（後続の空白/タブ許容）で終わる箇所は改行のみ削除
        text = re.sub(r",([ \t]*)\n", r",\1", text)
        return text.replace("\n", ",")

    if mode == "to_space":
        return text.replace("\n", " ")

    if mode == "remove":
        return text.replace("\n", "")

    # keep（未知の値も何もしない）
    return text


def sanitize_prompt(
    prompt,
    underscore_to_space=True,
    space_after_comma=True,
    remove_extra_comma=True,
    protect_lora=True,
    protect_score=True,
    newline_mode="keep",
    remove_duplicate_tags=False,
    strip_trailing_comma=False,
):
    """
    プロンプト文字列を整形する。各処理は対応する引数が有効なときのみ実行する。
    処理順: 改行正規化 → 保護退避 → 重複タグ削除 → newline_mode → アンダースコア変換
           → 余分カンマ除去 → カンマ正規化 → 末尾カンマ削除 → 保護復元
    """
    # 0. 改行コードを \n に統一
    text = prompt.replace("\r\n", "\n").replace("\r", "\n")

    # 1. 保護対象（LoRA等の <...> と Pony 品質タグ score_9 / score_8_up 等）を退避
    protected = []

    def _stash(match):
        protected.append(match.group(0))
        return f"\x00{len(protected) - 1}\x00"

    if protect_lora:
        text = re.sub(r"<[^>]*>", _stash, text)
    if protect_score:
        text = re.sub(r"score_\d+(?:_[a-zA-Z0-9]+)*", _stash, text)

    # 2. 重複タグ削除
    if remove_duplicate_tags:
        text = _remove_duplicate_tags(text, protected)

    # 3. 改行変換
    if newline_mode != "keep":
        text = _apply_newline_mode(text, newline_mode)

    # 4. アンダースコアを半角スペースへ変換
    if underscore_to_space:
        text = text.replace("_", " ")

    # 5. 連続する余分なカンマをまとめ、行頭のカンマを削除（改行は保持）
    if remove_extra_comma:
        text = re.sub(r",(?:[ \t]*,)+", ",", text)
        text = re.sub(r"(?m)^[ \t]*,[ \t]*", "", text)

    # 6. カンマ前後の空白を整理し ", " に統一（改行は保持）
    if space_after_comma:
        text = re.sub(r"[ \t]*,[ \t]*", ", ", text)

    # 7. 文字列全体の末尾のカンマ（連続・前後の空白/タブ込み）を削除。末尾の改行は保持
    if strip_trailing_comma:
        text = re.sub(r"([ \t]*,)+[ \t]*(?=\s*$)", "", text)

    # 8. 保護対象を復元
    text = _resolve_placeholders(text, protected)

    return text
