import torch
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
from scipy.ndimage import gaussian_filter

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
