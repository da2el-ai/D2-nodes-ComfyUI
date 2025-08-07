import sys
import os
import unittest
from datetime import datetime
import re

# 親ディレクトリをパスに追加して、モジュールをインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nodes.modules.template_util import replace_template, _get_date_str

class TestReplaceTemplate(unittest.TestCase):
    def test_date_pattern(self):
        """日付パターンの置換テスト"""
        now = datetime.now()
        template = "今日は%date:yyyy年MM月dd日%です"
        expected = f"今日は{now.strftime('%Y年%m月%d日')}です"
        result = replace_template(template)
        self.assertEqual(result, expected)
        
    def test_node_pattern(self):
        """ノードパターンの置換テスト"""
        template = "モデル: %node:1.model%"
        prompt = {
            "1": {
                "inputs": {
                    "model": "stable_diffusion_xl"
                }
            }
        }
        expected = "モデル: stable_diffusion_xl"
        result = replace_template(template, prompt=prompt)
        self.assertEqual(result, expected)
        
    def test_arg_pattern(self):
        """通常の引数パターンの置換テスト"""
        template = "ファイル名: %arg_1%"
        args = {"arg_1": "output.png"}
        expected = "ファイル名: output.png"
        result = replace_template(template, args=args)
        self.assertEqual(result, expected)
        
    def test_ckpt_name_pattern(self):
        """ckpt_nameパターンの置換テスト"""
        template = "モデル: %arg_1:ckpt_name%"
        args = {"arg_1": "model.safetensors"}
        expected = "モデル: model"
        result = replace_template(template, args=args)
        self.assertEqual(result, expected)
        
    def test_backslash_in_path(self):
        """バックスラッシュを含むパスの置換テスト"""
        template = "ファイルパス: %arg_1%"
        args = {"arg_1": r"D:\output\20250807-110634_00001_.png"}
        expected = r"ファイルパス: D:\output\20250807-110634_00001_.png"
        result = replace_template(template, args=args)
        self.assertEqual(result, expected)
        
    def test_backslash_in_ckpt_name(self):
        """バックスラッシュを含むパスのckpt_name置換テスト"""
        template = "モデルパス: %arg_1:ckpt_name%"
        args = {"arg_1": r"D:\models\stable_diffusion.safetensors"}
        expected = r"モデルパス: D:\models\stable_diffusion"
        result = replace_template(template, args=args)
        self.assertEqual(result, expected)
        
    def test_multiple_patterns(self):
        """複数のパターンが混在する場合のテスト"""
        now = datetime.now()
        template = "日付: %date:yyyyMMdd%, モデル: %node:1.model%, ファイル: %arg_1%, チェックポイント: %arg_2:ckpt_name%"
        prompt = {
            "1": {
                "inputs": {
                    "model": "stable_diffusion_xl"
                }
            }
        }
        args = {
            "arg_1": r"D:\output\image.png",
            "arg_2": "model.safetensors"
        }
        expected = f"日付: {now.strftime('%Y%m%d')}, モデル: stable_diffusion_xl, ファイル: D:\\output\\image.png, チェックポイント: model"
        result = replace_template(template, args=args, prompt=prompt)
        self.assertEqual(result, expected)
        
    def test_special_regex_chars(self):
        """正規表現の特殊文字を含む値の置換テスト"""
        template = "特殊文字: %arg_1%"
        args = {"arg_1": r"D:\output\file[1].png"}  # 角括弧は正規表現の特殊文字
        expected = r"特殊文字: D:\output\file[1].png"
        result = replace_template(template, args=args)
        self.assertEqual(result, expected)
        
    def test_none_value(self):
        """Noneの値の処理テスト"""
        template = "値: %arg_1%"
        args = {"arg_1": None}
        expected = "値: %arg_1%"  # Noneの場合は置換されない
        result = replace_template(template, args=args)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
