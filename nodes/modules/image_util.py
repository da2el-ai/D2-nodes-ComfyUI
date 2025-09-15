import torch
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
from scipy.ndimage import gaussian_filter
import os
import json
from comfy.cli_args import args
from PIL.PngImagePlugin import PngInfo
import piexif
import piexif.helper
from .util import D2_TD2Pipe




def tensor2pil(image):
    """
    Tensor to PIL
    """
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

def pil2tensor(image):
    """
    PIL to Tensor
    """
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

def convert_to_rgba_or_rgb(img, mode="rgba"):
    """
    RGBまたはRGBA形式に変換
    
    Args:
        img (torch.Tensor): 変換する画像 [height, width, channels]
        
    Returns:
        torch.Tensor: RGBA形式の画像 [height, width, 3 or 4]
    """
    # チャンネル数を取得
    if len(img.shape) < 3:
        raise ValueError("入力画像は少なくとも3次元である必要があります [height, width, channels]")

    channels = img.shape[-1]
    height, width = img.shape[0], img.shape[1]
    
    if mode == "rgba" and channels == 4:  # 既にRGBA
        return img
    elif mode == "rgb" and channels == 3:  # 既にRGB
        return img
    elif channels == 1:  
        # グレースケールをRGBに変換
        return img.repeat(1, 1, 3)
    elif mode == "rgba":
        # RGBをRGBAに変換
        result = torch.zeros((height, width, 4), dtype=img.dtype, device=img.device)
        result[:, :, :3] = img  # RGB部分をコピー
        result[:, :, 3] = 1.0   # アルファチャンネルは完全不透明に
        return result
    else:
        # RGBAをRGBに変換
        # 最初の3チャンネル（RGB部分）のみを取得
        return img[:, :, :3]  


def convert_batch_dimension(img, add_batch):
    """
    画像のバッチ次元を追加または削除する関数
    
    Args:
        img (torch.Tensor): 変換する画像
        add_batch (bool): True の場合、バッチ次元を追加。False の場合、バッチ次元を削除
        
    Returns:
        torch.Tensor: 次元を変換した画像
    """
    # 入力画像の次元数を確認
    dims = len(img.shape)
    
    if add_batch:
        # バッチ次元を追加する場合
        if dims == 3:  # [height, width, channels] -> [1, height, width, channels]
            return img.unsqueeze(0)
        elif dims == 4:  # すでに [batch, height, width, channels] の場合
            return img
        else:
            raise ValueError(f"予期しない入力形状: {img.shape}。3次元または4次元の画像を期待しています。")
    else:
        # バッチ次元を削除する場合
        if dims == 4:  # [batch, height, width, channels] -> [height, width, channels]
            if img.shape[0] != 1:
                raise ValueError(f"バッチサイズが1ではありません: {img.shape[0]}。次元削除はバッチサイズ1の場合のみ可能です。")
            return img.squeeze(0)
        elif dims == 3:  # すでに [height, width, channels] の場合
            return img
        else:
            raise ValueError(f"予期しない入力形状: {img.shape}。3次元または4次元の画像を期待しています。")


def apply_mosaic_to_image(image, dot_size, color_mode, brightness, invert_color):
    """
    単一の画像にモザイク効果を適用する
    
    Args:
        image: 入力画像テンソル [batch, height, width, channels] または [height, width, channels]
        dot_size: ドットの大きさ
        color_mode: 色のモード ("average" または "original")
        brightness: 明るさ調整 (-100 から 100)
        invert_color: 色を反転するかどうか
        
    Returns:
        モザイク効果を適用した画像テンソル
    """
    import torch
    
    # 画像の形状を取得
    shape = image.shape
    
    # バッチ次元がない場合（3次元テンソル）は一時的にバッチ次元を追加
    is_3d = len(shape) == 3
    if is_3d:
        # [height, width, channels] -> [1, height, width, channels]
        image = image.unsqueeze(0)
        shape = image.shape
        
    # ComfyUIの画像テンソルは [batch, height, width, channels] の形式
    batch_size, height, width, channels = shape
    
    # dot_sizeが1より小さい場合は1に制限
    dot_size = max(1, dot_size)
    
    # 結果画像の初期化
    mosaic_image = torch.zeros_like(image)
    
    # グリッドの数を計算（上限は切り上げて全体をカバー）
    grid_h = (height + dot_size - 1) // dot_size
    grid_w = (width + dot_size - 1) // dot_size
    
    # 各グリッドセルを処理
    for i in range(grid_h):
        for j in range(grid_w):
            # セルの範囲（画像の境界を超えないように制限）
            start_h = i * dot_size
            end_h = min(start_h + dot_size, height)
            start_w = j * dot_size
            end_w = min(start_w + dot_size, width)
            
            # セル内のピクセルを取得
            cell = image[:, start_h:end_h, start_w:end_w, :]
            
            if color_mode == "average":
                # セル内の色の平均を計算 (チャンネルごとに)
                avg_color = torch.mean(cell, dim=(1, 2))  # [batch_size, channels]
                cell_color = avg_color.unsqueeze(1).unsqueeze(2)  # [batch_size, 1, 1, channels]
            else:  # "original"
                # セルの中央のピクセルの色を使用（境界を超えないように）
                center_h = min(start_h + (end_h - start_h) // 2, height - 1)
                center_w = min(start_w + (end_w - start_w) // 2, width - 1)
                cell_color = image[:, center_h:center_h+1, center_w:center_w+1, :]
            
            # 明るさ調整
            if brightness != 0:
                # -100～100 の範囲を -1～1 に変換
                brightness_factor = brightness / 100.0
                if brightness_factor > 0:
                    # 明るくする（白に近づける）
                    cell_color = cell_color + (1 - cell_color) * brightness_factor
                else:
                    # 暗くする（黒に近づける）
                    cell_color = cell_color * (1 + brightness_factor)
            
            # 色を反転
            if invert_color:
                cell_color = 1.0 - cell_color
            
            # モザイクセルを結果画像に適用
            mosaic_image[:, start_h:end_h, start_w:end_w, :] = cell_color
        
    # 元の形状に戻す（3次元テンソルだった場合）
    if is_3d:
        mosaic_image = mosaic_image.squeeze(0)
        
    return mosaic_image


# 画像保存関数

def save_image(format, pil_image, file_path, compress_level=4, lossless=True, quality=80, prompt=None, extra_pnginfo=None, a1111_param=None):
    """
    PNG/JPEG/WEBP形式で画像を保存する
    
    Args:
        pil_image (PIL.Image): 保存する画像
        file_path (str): 保存先のファイルパス
        compress_level (int, optional): 圧縮レベル (0-9) / PNG用
        lossless (bool, optional): 可逆圧縮を使用するかどうか / WEBP用
        quality (int, optional): 画質 (0-100)、lossless=Falseの場合に使用 / JPEG・WEBP用
    """

    if format == "png":
        metadata = prepare_metadata_png(a1111_param, prompt, extra_pnginfo)

        if metadata is not None:
            pil_image.save(file_path, format="PNG", pnginfo=metadata, compress_level=compress_level)
        else:
            pil_image.save(file_path, format="PNG", compress_level=compress_level)

    elif format == "jpeg":
        metadata = prepare_metadata_exif(a1111_param, prompt, extra_pnginfo, pil_image)
        pil_image.save(file_path, exif=metadata, quality=quality)

    elif format == "webp":
        metadata = prepare_metadata_exif(a1111_param, prompt, extra_pnginfo, pil_image)
        pil_image.save(file_path, exif=metadata, lossless=lossless, quality=quality)


def save_image_animated_webp(pil_images, file_path, fps=6.0, lossless=True, quality=80, method=4, prompt=None, extra_pnginfo=None):
    """
    アニメーションWEBP形式で画像を保存する
    
    Args:
        pil_images (list): 保存する画像のリスト
        file_path (str): 保存先のファイルパス
        fps (float, optional): フレームレート
        metadata (PIL.Image.Exif, optional): メタデータ情報
        lossless (bool, optional): 可逆圧縮を使用するかどうか
        quality (int, optional): 画質 (0-100)、lossless=Falseの場合に使用
        method (int, optional): 圧縮方法 (0-6)
        
    Returns:
        str: 保存したファイルのパス
    """
    if len(pil_images) <= 1:
        raise ValueError("Cannot create animated WebP with only one image. Please provide multiple images for animation.")

    # メタデータの設定
    metadata = prepare_metadata_exif("", prompt, extra_pnginfo, pil_images[0])

    # 最初の画像を保存し、残りの画像を追加
    pil_images[0].save(
        file_path, 
        save_all=True, 
        duration=int(1000.0/fps), 
        append_images=pil_images[1:], 
        exif=metadata, 
        lossless=lossless, 
        quality=quality, 
        method=method
    )
    return file_path


def prepare_metadata_png(a1111_param=None, prompt=None, extra_pnginfo=None):
    """
    PNG形式のメタデータを準備する
    
    Args:
        prompt (dict, optional): プロンプト情報
        extra_pnginfo (dict, optional): 追加のメタデータ情報
        
    Returns:
        PngInfo: PNG形式のメタデータ
    """
    if args.disable_metadata:
        return None
    
    metadata = PngInfo()

    if prompt is not None:
        metadata.add_text("prompt", json.dumps(prompt))

    if extra_pnginfo is not None:
        for x in extra_pnginfo:
            metadata.add_text(x, json.dumps(extra_pnginfo[x]))

    if a1111_param is not None and a1111_param != "":
        metadata.add_text("parameters", a1111_param)

    return metadata


def prepare_metadata_exif(a1111_param=None, prompt=None, extra_pnginfo=None, base_image=None):
    """
    EXIF形式のメタデータを準備する
    
    Args:
        prompt (dict, optional): プロンプト情報
        extra_pnginfo (dict, optional): 追加のメタデータ情報
        base_image (PIL.Image, optional): メタデータのベースとなる画像
        
    Returns:
        PIL.Image.Exif: EXIF形式のメタデータ
    """
    if args.disable_metadata:
        return None

    # piexif の空Exif辞書を作る
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}

    if base_image is not None:
        try:
            exif_dict = piexif.load(base_image.info.get("exif", b""))
        except Exception:
            pass  # exifが無い場合は空のまま

    if prompt is not None:
        exif_dict["0th"][piexif.ImageIFD.Model] = "prompt:{}".format(json.dumps(prompt))

    
    if extra_pnginfo is not None:
        inital_exif = piexif.ImageIFD.Make
        for x in extra_pnginfo:
            exif_dict["0th"][inital_exif] = "{}:{}".format(x, json.dumps(extra_pnginfo[x]))
            inital_exif -= 1

    if a1111_param is not None and a1111_param != "":
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(a1111_param, "unicode")

    # dict → bytes に変換
    return piexif.dump(exif_dict)

