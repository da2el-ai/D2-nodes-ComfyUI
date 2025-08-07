import re
from datetime import datetime

"""
日付フォーマットを変換
"""
def _get_date_str(dt:datetime, pattern) -> str:
    # strftimeのフォーマットに変換
    format_str = pattern.replace('yyyy', '%Y')\
                      .replace('MM', '%m')\
                      .replace('dd', '%d')\
                      .replace('hh', '%H')\
                      .replace('mm', '%M')\
                      .replace('ss', '%S')
    
    # 日付文字列を生成して置換
    return dt.strftime(format_str)


"""
.safetensors 拡張子を削除する関数
"""
def _replace_ckpt_name(value: str) -> str:
    return value.replace('.safetensors', '')

"""
特定のノードから値を取得する
"""
def _get_node_value(prompt:dict, id_str:str, key:str) -> str:
    inputs = prompt[id_str]["inputs"]
    return str(inputs.get(key, ""))

"""
テンプレート文字列の置換を行う関数

Args:
    text (str): テンプレート文字列
    arg_1: 置換する値1
    arg_2: 置換する値2
    arg_3: 置換する値3

Returns:
    str: 置換後の文字列
"""
def replace_template(text: str, args={}, prompt={}) -> str:
    # 現在の日時を取得
    now = datetime.now()

    # date形式の置換 (%date:yyyyMMdd% 形式)
    def replace_date(match):
        pattern = match.group(1)
        return _get_date_str(now, pattern)
    text = re.sub(r'%date:([^%]+)%', replace_date, text)

    # ノードパターンの置換 (%node:ID.key% 形式)
    def replace_node(match):
        node_id = match.group(1)
        node_key = match.group(2)
        return _get_node_value(prompt, node_id, node_key)
    text = re.sub(r'%node:(\d+)\.([^%]+)%', replace_node, text)

    # 引数の置換
    for key, val in args.items():
        if val is not None:
            val_str = str(val)
            # ckpt_name パターンの置換 (%arg_N:ckpt_name%)
            ckpt_pattern = f'%{re.escape(key)}:ckpt_name%'
            ckpt_replacement = _replace_ckpt_name(val_str)
            text = re.sub(ckpt_pattern, lambda m: ckpt_replacement, text)
            
            # 通常の置換 (%arg_N%)
            normal_pattern = f'%{re.escape(key)}%'
            text = re.sub(normal_pattern, lambda m: val_str, text)
    return text
