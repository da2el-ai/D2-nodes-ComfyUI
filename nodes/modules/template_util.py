import re
from datetime import datetime
from . import util

"""
プリセットの配列を取得
"""
def _get_template_preset(preset_name):
    # 設定を読む
    config_path = util.get_config_path("template_config.yaml")
    config_sample_path = util.get_config_path("template_config.sample.yaml")
    config_value = util.load_config(config_path, config_sample_path)
    return config_value['preset'][preset_name]


"""
日付フォーマットを変換
"""
def _get_date_str(dt: datetime, pattern) -> str:
    # strftimeのフォーマットに変換
    format_str = (
        pattern.replace("yyyy", "%Y")
        .replace("MM", "%m")
        .replace("dd", "%d")
        .replace("hh", "%H")
        .replace("mm", "%M")
        .replace("ss", "%S")
    )

    # 日付文字列を生成して置換
    return dt.strftime(format_str)


"""
.safetensors 拡張子を削除する関数
"""
def _replace_ckpt_name(value: str) -> str:
    return value.replace(".safetensors", "")


"""
ノードIDから値を取得する
"""
def _get_node_value_from_id(prompt: dict, id_str: str, key: str) -> str:
    inputs = prompt[id_str]["inputs"]
    return str(inputs.get(key, ""))


"""
ノード名から値を取得する
"""
def _get_node_value_from_name(prompt: dict, name: str, key: str) -> str:
    # _meta.titleがnameと一致するノードを探す
    for node_id, node_data in prompt.items():
        meta = node_data.get("_meta", {})
        if meta.get("title") == name:
            # 一致するノードが見つかったら、inputsから指定されたキーの値を取得
            inputs = node_data.get("inputs", {})
            return str(inputs.get(key, ""))
    
    # 一致するノードが見つからない場合は空文字列を返す
    return ""

"""
プリセットに従って変換
"""
def _replace_template_preset(preset_name, val) -> str:
    """
    プリセットに従って変換する関数
    
    Args:
        preset_name (str): プリセット名
        val: 置換する値（配列・辞書・オブジェクトのいずれか）
        
    Returns:
        str: 置換後の文字列
    """
    # プリセットを取得
    preset_template = _get_template_preset(preset_name)
    
    # プリセットが見つからない場合は空文字列を返す
    if not preset_template:
        return ""
    
    # プリセットのテンプレートを置換
    result = preset_template
    
    # {arg.key} パターンの置換（オブジェクトの属性アクセス）
    def replace_attr(match):
        key = match.group(1)
        try:
            if hasattr(val, key):
                return str(getattr(val, key, ""))
            elif isinstance(val, dict) and key in val:
                return str(val[key])
            else:
                return ""
        except:
            return ""
    
    result = re.sub(r'\{arg\.([^}]+)\}', replace_attr, result)
    
    # {arg[index]} パターンの置換（配列のインデックスアクセス）
    def replace_index(match):
        index = int(match.group(1))
        try:
            if isinstance(val, (list, tuple)) and 0 <= index < len(val):
                return str(val[index])
            else:
                return ""
        except:
            return ""
    
    result = re.sub(r'\{arg\[(\d+)\]\}', replace_index, result)
    
    # {arg['key']} パターンの置換（辞書のキーアクセス）
    def replace_key(match):
        key = match.group(1)
        try:
            if isinstance(val, dict) and key in val:
                return str(val[key])
            else:
                return ""
        except:
            return ""
    
    result = re.sub(r'\{arg\[\'([^\']+)\'\]\}', replace_key, result)
    
    return result

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

    # date形式の置換 (%date:yyyyMMdd% 形式)
    now = datetime.now()
    def replace_date(match):
        pattern = match.group(1)
        return _get_date_str(now, pattern)

    text = re.sub(r"%date:([^%]+)%", replace_date, text)

    # ノードパターンの置換 (%node:ID.key% 形式)
    def replace_node_from_id(match):
        node_id = match.group(1)
        node_key = match.group(2)
        return _get_node_value_from_id(prompt, node_id, node_key)

    text = re.sub(r"%node:(\d+)\.([^%]+)%", replace_node_from_id, text)

    # 引数の置換（%arg_N%）
    for key, val in args.items():
        if val is not None:
            val_str = str(val)
            # ckpt_name パターンの置換 (%arg_N:ckpt_name%)
            ckpt_pattern = f"%{re.escape(key)}:ckpt_name%"
            ckpt_replacement = _replace_ckpt_name(val_str)
            text = re.sub(ckpt_pattern, lambda m: ckpt_replacement, text)

            # preset パターンの置換 (%arg_N:preset.{preset_name}%)
            def replace_preset(match):
                preset_name = match.group(1)
                return _replace_template_preset(preset_name, val)
                
            preset_pattern = f"%{re.escape(key)}:preset.([^%]+)%"
            text = re.sub(preset_pattern, replace_preset, text)

            # 通常の置換 (%arg_N%)
            normal_pattern = f"%{re.escape(key)}%"
            text = re.sub(normal_pattern, lambda m: val_str, text)

    # 引数の実行（%exec_N[0]%、%exec_N.steps%、%exec_N['foo']%）
    """
    - args に登録されているアイテムに対し、pythonのListやDictの値取得を実行する
    - text から `%exec_1[0]%`,`%exec_1['foo']%`,`%exec_1.bar%` などのパターンを抽出
    - `exec_1` は `args['arg_1']` に該当する
    - `args['arg_1'] = [100, 200, 300]` の時に `%exec_1[0]%` を検知したら `100` と置き換える
    - `args['arg_2'] = `{'foo':'bar'}` の時に `%exec_2['foo']%` を検知したら `bar` と置き換える
    """
    # リストインデックスアクセス (%exec_N[0]% 形式)
    def replace_exec_index(match):
        arg_num = match.group(1)
        index = int(match.group(2))
        arg_key = f"arg_{arg_num}"
        
        if arg_key in args and args[arg_key] is not None:
            try:
                return str(args[arg_key][index])
            except (IndexError, TypeError, KeyError):
                return ""
        return ""

    text = re.sub(r"%exec_(\d+)\[(\d+)\]%", replace_exec_index, text)

    # 辞書キーアクセス (%exec_N['foo']% 形式)
    def replace_exec_key(match):
        arg_num = match.group(1)
        key = match.group(2)
        arg_key = f"arg_{arg_num}"
        
        if arg_key in args and args[arg_key] is not None:
            try:
                return str(args[arg_key][key])
            except (TypeError, KeyError):
                return ""
        return ""

    text = re.sub(r"%exec_(\d+)\['([^']+)'\]%", replace_exec_key, text)

    # 属性アクセス (%exec_N.attribute% 形式)
    def replace_exec_attr(match):
        arg_num = match.group(1)
        attr = match.group(2)
        arg_key = f"arg_{arg_num}"
        
        if arg_key in args and args[arg_key] is not None:
            try:
                return str(getattr(args[arg_key], attr, ""))
            except (TypeError, AttributeError):
                return ""
        return ""

    text = re.sub(r"%exec_(\d+)\.([a-zA-Z0-9_]+)%", replace_exec_attr, text)

    # ノードパターンの置換 (%ノード名.key% 形式)
    def replace_node_from_name(match):
        node_name = match.group(1)
        node_key = match.group(2)
        return _get_node_value_from_name(prompt, node_name, node_key)

    text = re.sub(r"%([^\.%]+)\.([^%]+)%", replace_node_from_name, text)

    return text
