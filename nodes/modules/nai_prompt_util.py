"""
StableDiffusion 方式と NovelAI 方式のプロンプト weight 相互変換の純ロジック。
ComfyUI 非依存にして単体テスト（test/test_nai_prompt_util.py）できるようにする。
web/D2_PromptConverDialog.js にも同じロジックがあるので、変更するときは両方を揃える。
"""
import math
import re


CONVERT_TYPES = ["sd_to_nai", "nai_to_sd"]
MODES = ["number", "brace"]

# ブレース1個あたりの倍率
BRACE_RATE = 1.05

# SD 方式の weight 指定 (text:1.2)
SD_WEIGHT_PATTERN = re.compile(r"\(([^)]+):\s*(-?\d*\.?\d+)\s*\)")
# NAI 方式の weight 開始 1.2:: と閉じ ::
# 直前が英数字・_・. のときは aaa5:: や 2girls:: の語の一部なので weight 開始とみなさない
NAI_NUMBER_TOKEN_PATTERN = re.compile(r"(?<![\w.])(-?\d*\.?\d+)::|::")
# NAI 方式のブレース {{aaa}} [[aaa]]
NAI_BRACE_PATTERN = re.compile(r"[\[{]+[^\]}]+[\]}]+")
# weight 本文を 先頭の空白 / 中身 / 末尾の空白・カンマ に分ける
BODY_PATTERN = re.compile(r"^(\s*)(.*?)([\s,]*)$", re.DOTALL)


"""
weight を JS の String(number) と同じ表記にする（1.40 → 1.4、1.0 → 1）
"""
def format_weight(weight):
    if weight == int(weight):
        return str(int(weight))
    return repr(weight)


"""
JS の Math.round と同じ丸め（Python の round は偶数丸めなので使わない）
"""
def js_round(value):
    return math.floor(value + 0.5)


"""
行ごとに変換関数を適用する（weight の範囲は改行を越えない）
"""
def _convert_lines(prompt, convert_line):
    return "\n".join(convert_line(line) for line in prompt.split("\n"))


"""
SD 方式を NAI 方式に変換する
"""
def convert_to_nai(prompt, mode="number"):
    return _convert_lines(prompt, lambda line: SD_WEIGHT_PATTERN.sub(
        lambda m: _sd_weight_to_nai(m.group(1).strip(), float(m.group(2)), mode), line
    ))


"""
(text:weight) 1個を NAI 方式に変換する
"""
def _sd_weight_to_nai(text, weight, mode):
    # ブレース方式は weight 0 以下を log で表せないので数値方式で出す
    if mode == "number" or weight <= 0:
        # 閉じ :: の直前が数字だと aaa5:: の 5:: が weight 開始と誤解釈されるので空白を入れる
        return f"{format_weight(weight)}::{text} ::"

    count = abs(js_round(math.log(weight) / math.log(BRACE_RATE)))
    if weight < 1:
        return "[" * count + text + "]" * count
    return "{" * count + text + "}" * count


"""
NAI 方式を SD 方式に変換する
"""
def convert_to_sd(prompt, mode="number", remove_negative=True):
    if mode == "number":
        return _convert_lines(prompt, lambda line: _nai_number_line_to_sd(line, remove_negative))
    return _convert_lines(prompt, lambda line: NAI_BRACE_PATTERN.sub(
        lambda m: _nai_brace_to_sd(m.group(0)), line
    ))


"""
数値方式の1行を SD 方式に変換する。
weight 開始と閉じ :: を先頭から順に拾い、閉じ忘れは次の weight 開始か行末で閉じる。
"""
def _nai_number_line_to_sd(line, remove_negative):
    result = []
    pos = 0
    open_weight = None

    for m in NAI_NUMBER_TOKEN_PATTERN.finditer(line):
        body = line[pos:m.start()]
        if m.group(1) is None and open_weight is not None:
            # 閉じ :: 直前の空白は sd_to_nai が誤解釈防止で入れたものなので捨てる
            body = body.rstrip()
        result.append(_close_weight(body, open_weight, remove_negative))
        if m.group(1) is not None:
            open_weight = float(m.group(1))
        elif open_weight is not None:
            open_weight = None
        else:
            # 対応する weight 開始がない :: は文字として残す
            result.append("::")
        pos = m.end()

    result.append(_close_weight(line[pos:], open_weight, remove_negative))
    return "".join(result)


"""
weight の本文を (text:weight) にする。weight が開いていなければ本文をそのまま返す。
"""
def _close_weight(body, weight, remove_negative):
    if weight is None:
        return body

    lead, text, trail = BODY_PATTERN.match(body).groups()
    if text == "" or (weight < 0 and remove_negative):
        return lead + trail
    return f"{lead}({text}:{format_weight(weight)}){trail}"


"""
ブレース方式 {{aaa}} [[aaa]] 1個を SD 方式に変換する
"""
def _nai_brace_to_sd(prompt):
    count = len(re.findall(r"[\[{]", prompt))
    if prompt[0] == "{":
        weight = BRACE_RATE ** count
    else:
        weight = (1 / BRACE_RATE) ** count

    weight = js_round(weight * 10) / 10
    text = re.sub(r"[\[\]{}]+", "", prompt)
    return f"({text}:{format_weight(weight)})"
