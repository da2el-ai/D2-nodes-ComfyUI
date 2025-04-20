import json
import re
import requests
from PIL import Image, PngImagePlugin
import piexif
import piexif.helper



#
# 画像からプロンプトを取り出す
#
# @return {positive:str, negative:str}
#
def get_prompt(img:Image.Image) -> dict[str, str]:

  prompt = {'positive':'', 'negative':''}
  items = (img.info or {}).copy()
  # print("items ///////////////")
  # print(items)

  if "exif" in items:
    exif = img.info['exif']

    exif_data = piexif.load(exif)
    # print("exif_data------")
    # print(exif_data)
    # print(extract_and_format_exif(exif_data))
    # print("////////////")
    # print("Exif--------")
    # print(exif_data.get('Exif'))

    exif_comment = (exif_data or {}).get('Exif', {}).get(piexif.ExifIFD.UserComment, b'')
    # print("exif_coment------")
    # print(exif_comment)

    if exif_comment:
        try:
            comment = piexif.helper.UserComment.load(exif_comment)
        except Exception as e:
            return prompt
    else:
        return prompt

    if 'Script: Kohaku NAI Client' in comment:
      # print("TYPE: kohaku")
      (prompt['positive'], prompt['negative']) = _get_prompt_kohaku(comment)

    elif 'Steps: ' in comment:
      # print("TYPE: a1111")
      (prompt['positive'], prompt['negative']) = _get_prompt_a1111(comment)

  elif "workflow" in items:
    # print("TYPE: comfy")
    (prompt['positive'], prompt['negative']) = _get_prompt_comfy(items)

  elif items.get("Software", None) == "NovelAI":
    # print("TYPE: nai")
    (prompt['positive'], prompt['negative']) = _get_prompt_nai(items)

  elif "parameters" in items:
    # print("assuming A1111-style parameters")
    comment = items["parameters"]
    (prompt['positive'], prompt['negative']) = _get_prompt_a1111(comment)

  return prompt

# 
# 0th.model だけ整形
# 
def format_model_json(exif_data):
    try:
        # 0thセクションからmodelフィールドを取得
        model_data = exif_data['0th'].get(piexif.ImageIFD.Model)
        
        if model_data is None:
            return "No model data found in Exif."
        
        # バイト文字列をデコード
        if isinstance(model_data, bytes):
            model_data = model_data.decode('utf-8', errors='replace')

        model_data = re.sub(r'^prompt:', '', model_data.strip())
        
        # 最初の '{' から最後の '}' までを抽出
        
        json_match = re.search(r'\{.*\}', model_data, re.DOTALL)
        if json_match:
            json_string = json_match.group()

        # JSON文字列をPythonオブジェクトにパース
        model_json = json.loads(json_string)
        
        # 整形されたJSONを返す
        return json.dumps(model_json, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        return "Error: The model data is not valid JSON."
    except Exception as e:
        return f"Error processing model data: {str(e)}"


#
# JSONを整形して出力
#
def extract_and_format_exif(exif_data):
    try:
        # Exifデータを人間が読める形式に変換
        readable_exif = {}
        for ifd in exif_data:
            if ifd == "thumbnail":
                continue
            readable_exif[ifd] = {}
            for tag_id, value in exif_data[ifd].items():
                try:
                    tag = piexif.TAGS[ifd][tag_id]["name"]
                except KeyError:
                    tag = f"Unknown_{tag_id}"
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except UnicodeDecodeError:
                        value = value.decode('utf-8', errors='replace')
                readable_exif[ifd][tag] = value

        # JSONとして整形
        return json.dumps(readable_exif, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error processing Exif data: {str(e)}"


#
# KohakuNAI 画像からプロンプト取得
#
def _get_prompt_kohaku(comment:str):
  comment = comment.split(', Script: Kohaku NAI', 1)[0]

  # KohakuNAIのバージョンによってPNGinfoが違うぽいので対応
  try:
    json_info = json.loads(comment)

    return (
      json_info.get('input', ''),
      json_info.get('parameters',{}).get('negative_prompt', '')
    )
  except:
    params = re.split(r'Negative prompt: *|Steps: ', comment)

    return (
      params[0],
      params[1] if 'Negative prompt:' in comment else ''
    )


#
# webui a1111 画像からプロンプト取得
#
def _get_prompt_a1111 (comment:str):
  params = re.split(r'Negative prompt: *|Steps: ', comment)

  return (
    params[0],
    params[1] if 'Negative prompt:' in comment else ''
  )

#
# NovelAI 画像からプロンプト取得
#
def _get_prompt_nai(items:dict):
  json_info = json.loads(items["Comment"])

  return (
    json_info.get('prompt', ''),
    json_info.get('uc','')
  )


#
# ComfyUI 画像からプロンプト取得
#
def _get_prompt_comfy(items:dict):
  try:
    info = json.loads(items.get('prompt', {}))
    # print("prompt")
    # print(json.dumps(info, indent=2, ensure_ascii=False))
  except json.JSONDecodeError:
    return '',''

  if not isinstance(info, dict):
    return '',''

  for id_str, val in info.items():
     if 'KSampler' in val['class_type']:
        positive = _extract_comfy_prompt(info, id_str, 'positive')
        negative = _extract_comfy_prompt(info, id_str, 'negative')
        return positive, negative

  return '',''

def _extract_comfy_prompt(info:dict, id_str:str, type:str):
  # print("_extract_comfy_prompt ---")
  # print(json.dumps(info[id_str]['inputs'], indent=2, ensure_ascii=False))

  # inputs から text または positive/negative を探す
  # 内容が文字列だったらプロンプトだと判断
  # list だったらさらに辿る
  for key, val in info[id_str]['inputs'].items():
    # print("key - ", key)
    if type in key or "text" in key:
      if isinstance(val, str):
         return val
      elif isinstance(val, list):
        return _extract_comfy_prompt(info, val[0], type)
      
  return ""
