"""
CSV / TSV パース・整形の純ロジック。
ComfyUI 非依存にして単体テスト（test/test_csv_util.py）できるようにする。
"""
import csv
import io
import re


# file_type → 区切り文字
DELIMITERS = {
    "csv": ",",
    "tsv": "\t",
}


def parse_range(index_str, axis="row"):
    """
    範囲指定文字列を (start, end) の1スタート・両端含むタプルへ変換する。
    - "" （無指定）        -> None（全件）
    - "3"                 -> (3, 3)
    - "2-"                -> (2, None)   None は「最後まで」
    - "-4"                -> (1, 4)
    - "2-4"               -> (2, 4)
    壊れた書式（非数値・`2--4`・`0`・`-` 単体 等）は ValueError を投げる。
    axis はエラーメッセージ用（"row" / "column"）。
    """
    s = (index_str or "").strip()
    if s == "":
        return None

    def _err():
        return ValueError(f"{axis}_index の書式が不正です: '{index_str}'")

    # 単一の数値
    if re.fullmatch(r"\d+", s):
        n = int(s)
        if n < 1:
            raise _err()
        return (n, n)

    # `開始-終了`（どちらか省略可）。ハイフンは1つだけ
    m = re.fullmatch(r"(\d*)-(\d*)", s)
    if not m:
        raise _err()

    left, right = m.group(1), m.group(2)
    if left == "" and right == "":
        # "-" 単体は不正
        raise _err()

    start = int(left) if left != "" else 1
    end = int(right) if right != "" else None
    if start < 1 or (end is not None and end < 1):
        raise _err()

    return (start, end)


def slice_range(seq, rng):
    """1スタート・両端含む範囲を 0スタートの seq に適用する。範囲外・開始>終了は空。"""
    if rng is None:
        return list(seq)
    start, end = rng
    # 1スタート両端含む [start, end] -> 0スタートスライス [start-1 : end]
    return list(seq)[start - 1:] if end is None else list(seq)[start - 1:end]


def _format_csv_text(rows, use_doublequote):
    """2次元配列を「行=改行・セル=カンマ」のテキストにする。出力区切りは常にカンマ。"""
    if use_doublequote:
        # 全セルをダブルクォート（QUOTE_ALL 相当。セル内の " は "" にエスケープ）
        lines = []
        for row in rows:
            buf = io.StringIO()
            csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="").writerow(row)
            lines.append(buf.getvalue())
        return "\n".join(lines)
    # クォートせず素のカンマ結合（カンマを含むセルは区切りが失われる＝仕様どおり）
    return "\n".join(",".join(row) for row in rows)


def load_csv(text, file_type="csv", output_mode="list", row_index="", column_index="", use_doublequote=True):
    """
    CSV/TSV テキストを範囲選択して出力する。
    返り値: (output, lines_count)
      - output: output_mode="list" なら 2次元配列、"csv" ならテキスト
      - lines_count: 選択範囲（row_index 適用後）の行数
    row_index / column_index の書式が壊れていれば ValueError（ワークフロー停止用）。
    """
    row_range = parse_range(row_index, axis="row")
    col_range = parse_range(column_index, axis="column")

    delimiter = DELIMITERS.get(file_type, ",")

    selected = []
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    for i, row in enumerate(reader, start=1):  # 1スタートのレコード番号
        if row_range is not None:
            start, end = row_range
            if i < start:
                continue
            if end is not None and i > end:
                break  # 終端が決まっていれば以降は読まない（巨大ファイルの早期打ち切り）
        # 列範囲を適用して保持
        selected.append(slice_range(row, col_range))

    lines_count = len(selected)

    if output_mode == "csv":
        output = _format_csv_text(selected, use_doublequote)
    else:  # list
        output = selected

    return output, lines_count
