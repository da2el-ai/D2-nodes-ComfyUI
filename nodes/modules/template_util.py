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
def replace_template(text: str, arg_1=None, arg_2=None, arg_3=None, prompt={}) -> str:
    # 現在の日時を取得
    now = datetime.now()
    
    # date形式の置換
    # %date:yyyyMMdd% 形式を検索
    date_patterns = re.findall(r'%date:([^%]+)%', text)
    for pattern in date_patterns:
        text = text.replace(f'%date:{pattern}%', _get_date_str(now, pattern))

    # ノードパターンの置換
    if node_pattern := re.search('%node:(\d+)\.([^%]+)%', text):
        node_id = node_pattern.group(1)  # 数字部分を取得
        node_key = node_pattern.group(2)  # キー部分を取得
        pattern = f'%node:{node_id}.{node_key}%'
        text = text.replace(pattern, _get_node_value(prompt, node_id, node_key))

    # 引数の置換
    for key in ["arg_1", "arg_2", "arg_3"]:
        val = locals()[key]

        if val is not None:
            # ckpt_name パターンの置換
            if f'%{key}:ckpt_name%' in text:
                text = text.replace(f'%{key}:ckpt_name%', _replace_ckpt_name(str(val)))

            # 通常の置換
            text = text.replace(f'%{key}%', str(val))
    
    return text