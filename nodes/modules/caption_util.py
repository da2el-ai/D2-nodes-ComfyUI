import os
import re
from collections import Counter


# exclude_tags の正規表現エントリ書式: regex/pattern/
REGEX_ENTRY_PATTERN = re.compile(r"^regex/(.*)/$")

# レポートのコメント行: 行頭（空白許容）が // または #
COMMENT_PATTERN = re.compile(r"^\s*(?://|#)\s*")

# レポート行末尾の出現回数: ",数値"
COUNT_PATTERN = re.compile(r",\s*\d+\s*$")


"""
テキストファイルを読み込む
- ファイルが存在しない場合は空文字を返す（キャプション未作成の画像が混ざるケースに対応）
- encode_to_utf8=True なら charset-normalizer で文字コードを自動判別して utf-8 に変換
- False なら変換せず utf-8 として読む（デコード不能文字は置換してクラッシュを避ける）
"""
def load_text_file(file_path, encode_to_utf8=False) -> str:
    if not file_path or not os.path.isfile(file_path):
        return ""

    if encode_to_utf8:
        # 依存が無い環境でも他機能が動くよう遅延 import
        from charset_normalizer import from_path
        best = from_path(file_path).best()
        return str(best) if best is not None else ""

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


"""
exclude_tags / レポート編集文をエントリのリストにパースする
- カンマ・改行の両方で区切る
- ただし行全体が regex/pattern/ 形式の行は1エントリとして扱う
  （正規表現内のカンマ {2,3} 等をカンマ分割で壊さないため。regex エントリは1行1つで書く想定）
"""
def parse_exclude_tags(exclude_text) -> list[str]:
    entries = []
    for line in exclude_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if REGEX_ENTRY_PATTERN.match(line):
            entries.append(line)
        else:
            entries.extend(tag.strip() for tag in line.split(",") if tag.strip())
    return entries


"""
exclude エントリから (完全一致セット, コンパイル済み正規表現リスト) を作る
- replace_underscore=True ならエントリ側にも underscore 置換を適用してから比較する
  （タグレポート由来の `_` 付きタグが不一致にならないように）
- 不正な正規表現はスキップして警告を出す
"""
def _build_exclude_matchers(exclude_text, replace_underscore, ignore_case):
    exact_set = set()
    regex_list = []
    flags = re.IGNORECASE if ignore_case else 0

    for entry in parse_exclude_tags(exclude_text):
        match = REGEX_ENTRY_PATTERN.match(entry)
        if match:
            try:
                regex_list.append(re.compile(match.group(1), flags))
            except re.error as e:
                print(f"[D2 Save Caption] 不正な正規表現をスキップ: {entry} ({e})")
        else:
            if replace_underscore:
                entry = entry.replace("_", " ")
            exact_set.add(entry.lower() if ignore_case else entry)

    return exact_set, regex_list


"""
キャプションのタグ整形
処理順: 分割 → trim → underscore置換 → exclude除去 → 重複除去 → prepend → trailing_comma → 結合
"""
def format_caption(text, exclude_tags="", prepend_tags="", replace_underscore=False, trailing_comma=False, ignore_case=True) -> str:
    # 分割・trim（空要素は捨てる）
    tags = [tag.strip() for tag in text.split(",")]
    tags = [tag for tag in tags if tag]

    # underscore 置換
    if replace_underscore:
        tags = [tag.replace("_", " ") for tag in tags]

    # exclude 除去（通常エントリは完全一致、regex/pattern/ は re.search）
    exact_set, regex_list = _build_exclude_matchers(exclude_tags, replace_underscore, ignore_case)

    def is_excluded(tag):
        key = tag.lower() if ignore_case else tag
        if key in exact_set:
            return True
        return any(regex.search(tag) for regex in regex_list)

    tags = [tag for tag in tags if not is_excluded(tag)]

    # 重複除去（先勝ち。大小の扱いは ignore_case に従う）
    seen = set()
    unique_tags = []
    for tag in tags:
        key = tag.lower() if ignore_case else tag
        if key not in seen:
            seen.add(key)
            unique_tags.append(tag)

    # prepend（既にあるタグは追加しない。判定は exclude と同じ正規化・大小規則）
    prepend_list = [tag.strip() for tag in prepend_tags.split(",") if tag.strip()]
    if replace_underscore:
        prepend_list = [tag.replace("_", " ") for tag in prepend_list]

    existing = {tag.lower() if ignore_case else tag for tag in unique_tags}
    prepended = []
    for tag in prepend_list:
        key = tag.lower() if ignore_case else tag
        if key not in existing:
            existing.add(key)
            prepended.append(tag)

    # 結合
    result = ", ".join(prepended + unique_tags)
    if trailing_comma and result:
        result += ","
    return result


"""
キャプションをファイルに保存する
- base_filename の拡張子を extension に置換したパスに保存（d:/images/aaa.jpg → d:/images/aaa.txt）
- backup=True なら既存ファイルを <保存パス>.bak にリネーム（.bak が既にあれば上書き）
- 保存先のフルパスを返す
- base_filename が空だと ".txt" 等の相対パスがカレントディレクトリに書かれてしまう。
  キャプション付けは大量処理のため、間違いに気づかず全件無駄になるのを防ぐべく
  空の場合は ValueError で停止する（キューは ComfyUI 本体の中止ボタンで止める想定）
- dry_run=True なら書き込み・バックアップをせず、保存予定パスだけ返す（変換結果の確認用）。
  この場合 base_filename が空でもエラーにせず空文字を返す（保存しないため）
"""
def save_caption(base_filename, text, extension="txt", backup=True, dry_run=False) -> str:
    if not base_filename or not base_filename.strip():
        if dry_run:
            return ""
        raise ValueError("D2 Save Caption: base_filename が空です。保存先を特定できないため停止しました。")

    save_path = os.path.splitext(base_filename)[0] + "." + extension

    if dry_run:
        return save_path

    if backup and os.path.isfile(save_path):
        bak_path = save_path + ".bak"
        if os.path.isfile(bak_path):
            os.remove(bak_path)
        os.rename(save_path, bak_path)

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(text)

    return save_path


"""
キャプションファイル群からタグの出現回数を集計する
- カンマ・改行をタグ区切りとして数える
- order_by: count_9-0（多い順）/ count_0-9（少ない順）/ tag_a-z / tag_z-a
- (タグ, 回数) のリストを返す
"""
def count_tags(file_list, order_by="count_9-0") -> list[tuple[str, int]]:
    counter = Counter()
    for file_path in file_list:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError:
            continue
        for tag in content.replace("\n", ",").split(","):
            tag = tag.strip()
            if tag:
                counter[tag] += 1

    items = list(counter.items())
    if order_by == "count_0-9":
        items.sort(key=lambda x: (x[1], x[0]))
    elif order_by == "tag_a-z":
        items.sort(key=lambda x: x[0])
    elif order_by == "tag_z-a":
        items.sort(key=lambda x: x[0], reverse=True)
    else:  # count_9-0（デフォルト）
        items.sort(key=lambda x: (-x[1], x[0]))
    return items


"""
集計結果を表示用レポート（1行 タグ,回数）に整形する
"""
def build_tag_report(items, without_count=False) -> str:
    if without_count:
        return "\n".join(tag for tag, _ in items)
    return "\n".join(f"{tag},{count}" for tag, count in items)


"""
編集後レポートを exclude_tags 用のタグリストに整形する
- remove_comment: コメント行（// #）を捨てて残りを採用
- output_comment: コメント行のみ採用（コメント記号は除去）
- 各行から末尾の ",出現回数" を除去して結合する
- separator: "newline" なら改行区切り、"comma" ならカンマ＋空白区切り
  改行区切りは 1タグ1行になるので、手書きの regex/a{2,3}/ のような
  カンマを含む正規表現エントリが分割されず保護される
"""
def format_tag_report(text, output_type="remove_comment", separator="newline") -> str:
    tags = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        is_comment = bool(COMMENT_PATTERN.match(stripped))

        if output_type == "output_comment":
            if not is_comment:
                continue
            entry = COMMENT_PATTERN.sub("", stripped)
        else:  # remove_comment
            if is_comment:
                continue
            entry = stripped

        entry = COUNT_PATTERN.sub("", entry).strip()
        if entry:
            tags.append(entry)

    joiner = "\n" if separator == "newline" else ", "
    return joiner.join(tags)
