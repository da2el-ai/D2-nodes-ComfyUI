import torch
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
from scipy.ndimage import gaussian_filter

def apply_mask_to_image(img, mask):
    """
    マスクを画像に適用する
    
    Args:
        img (torch.Tensor): 適用する画像 [height, width, channels]
        mask (torch.Tensor): 適用するマスク [height, width]
        
    Returns:
        torch.Tensor: マスクが適用された画像 [height, width, 4] (RGBA)
    """
    # チャンネル数を取得
    channels = img.shape[-1]
    rect_height, rect_width = img.shape[0], img.shape[1]
    
    # マスクで切り抜く - RGBA形式を確保
    if channels == 4:  # 既にRGBA
        # マスクをアルファチャンネルとして適用
        result = img.clone()
        result[:, :, 3] = result[:, :, 3] * mask
    else:  # RGBをRGBAに変換
        # 新しいRGBA画像を作成
        result = torch.zeros((rect_height, rect_width, 4), dtype=img.dtype, device=img.device)
        result[:, :, :3] = img  # RGB部分をコピー
        
        # マスクの形状を確認して適切に適用
        if mask.shape[0] == rect_height and mask.shape[1] == rect_width:
            result[:, :, 3] = mask  # マスクをアルファとして使用
        else:
            print(f"Mask crop shape mismatch: mask={mask.shape}, rect={rect_height}x{rect_width}")
            # 簡易的な対応: 一律透明度を適用
            result[:, :, 3] = 1.0
    
    return result



def adjust_mask_dimensions(mask):
    """
    マスクの次元を確認して調整する
    
    Args:
        mask (torch.Tensor): 調整するマスク
        
    Returns:
        torch.Tensor: 調整されたマスク
    """
    # マスクの次元を確認して調整
    if len(mask.shape) == 3 and mask.shape[0] == 1:
        # バッチ次元のあるマスク [1, height, width] → [height, width]
        mask = mask.squeeze(0)
        # print(f"Adjusted mask shape: {mask.shape}")
    
    return mask



def check_mask_image_compatibility(mask, height, width):
    """
    マスク形状が画像に合っているか確認し、必要に応じて調整する
    
    Args:
        mask (torch.Tensor): 確認するマスク
        height (int): 画像の高さ
        width (int): 画像の幅
        
    Returns:
        torch.Tensor: 調整されたマスク
    """
    if mask.shape[0] != height or mask.shape[1] != width:
        print(f"Warning: Image dimensions ({height}x{width}) and mask dimensions ({mask.shape[0]}x{mask.shape[1]}) don't match.")
        # 幅と高さが入れ替わっていたら差し換える
        if mask.shape[0] == width and mask.shape[1] == height:
            mask = mask.transpose(0, 1)
            print(f"Transposed mask shape: {mask.shape}")
        # 他のケースでのリサイズ処理も必要に応じて追加
    
    return mask



def convert_to_rgba(img):
    """
    RGBまたはRGBA画像を確実にRGBA形式に変換
    
    Args:
        img (torch.Tensor): 変換する画像 [height, width, channels]
        
    Returns:
        torch.Tensor: RGBA形式の画像 [height, width, 4]
    """
    # チャンネル数を取得
    channels = img.shape[-1]
    height, width = img.shape[0], img.shape[1]
    
    if channels == 4:  # 既にRGBA
        return img
    else:  # RGBをRGBAに変換
        # 新しいRGBA画像を作成
        result = torch.zeros((height, width, 4), dtype=img.dtype, device=img.device)
        result[:, :, :3] = img  # RGB部分をコピー
        result[:, :, 3] = 1.0   # アルファチャンネルは完全不透明に
        return result


def apply_simple_inner_feathering(mask, feather_radius):
    """
    シンプルな内側フェザリング
    
    Args:
        mask (torch.Tensor): ぼかすマスク [height, width]
        feather_radius (int): ぼかす範囲のピクセル数
        
    Returns:
        torch.Tensor: 内側だけぼかしたマスク [height, width]
    """
    if feather_radius <= 0:
        return mask
    
    # マスクをNumPyに変換
    mask_np = mask.cpu().numpy()
    original_mask = mask_np.copy()
    
    # マスクを収縮
    from scipy.ndimage import binary_erosion
    structure = np.ones((3, 3))  # 3x3 構造要素
    eroded_mask = original_mask
    # フェザー半径に応じてエロージョンを繰り返す
    iterations = max(1, feather_radius // 2)
    eroded_mask = binary_erosion(original_mask, structure=structure, iterations=iterations)
    
    # 収縮したマスクをぼかす
    blurred_mask = gaussian_filter(eroded_mask.astype(float), sigma=feather_radius/2)
    
    # 元のマスクの範囲内だけを使用
    result_mask = np.where(original_mask > 0, blurred_mask, 0)
    
    # 結果をTensorに戻す
    return torch.from_numpy(result_mask).to(mask.device)



def apply_distance_inner_feathering(mask, feather_radius):
    """
    距離に基づく内側フェザリング
    
    Args:
        mask (torch.Tensor): ぼかすマスク [height, width]
        feather_radius (int): ぼかす範囲のピクセル数
        
    Returns:
        torch.Tensor: 内側だけぼかしたマスク [height, width]
    """
    if feather_radius <= 0:
        return mask
    
    # マスクをNumPyに変換
    mask_np = mask.cpu().numpy()
    original_mask = mask_np.copy()
    
    # 距離マップを計算（マスク内部の各ピクセルと境界との最短距離）
    from scipy.ndimage import distance_transform_edt
    distance_map = distance_transform_edt(mask_np)
    
    # フェザリング領域を定義（距離がフェザー半径以下の領域）
    feather_region = (distance_map <= feather_radius) & (distance_map > 0)
    
    # フェザリング係数を計算（距離に応じて0〜1）
    feather_factor = distance_map / feather_radius
    feather_factor = np.clip(feather_factor, 0, 1)
    
    # フェザリング係数を適用
    result_mask = original_mask.copy()
    result_mask[feather_region] = result_mask[feather_region] * feather_factor[feather_region]
    
    # 結果をTensorに戻す
    return torch.from_numpy(result_mask).to(mask.device)


def apply_feathering(mask, feather_radius, feather_type="simple"):
    """
    マスクのエッジをぼかす
    
    Args:
        mask (torch.Tensor): ぼかすマスク [height, width]
        feather_radius (int): ぼかす範囲のピクセル数
        feather_type (str): フェザリングのタイプ
            - "simple": シンプルな内側フェザリング
            - "distance": 距離に基づく内側フェザリング
            
    Returns:
        torch.Tensor: ぼかしたマスク [height, width]
    """
    if feather_radius <= 0:
        return mask
    
    if feather_type == "simple":
        return apply_simple_inner_feathering(mask, feather_radius)
    elif feather_type == "distance":
        return apply_distance_inner_feathering(mask, feather_radius)
    else:
        # デフォルトの処理：両方向にぼかす
        mask_np = mask.cpu().numpy()
        mask_blurred = gaussian_filter(mask_np, sigma=feather_radius/2)
        return torch.from_numpy(mask_blurred).to(mask.device)




def adjust_rectangle_dimensions(x_min, y_min, x_max, y_max, width, height, padding=0, min_width=0, min_height=0):
    """
    矩形領域の寸法を調整する
    
    Args:
        x_min (int): 矩形の左端のX座標
        y_min (int): 矩形の上端のY座標
        x_max (int): 矩形の右端のX座標
        y_max (int): 矩形の下端のY座標
        width (int): 画像の幅
        height (int): 画像の高さ
        padding (int): 矩形を拡張するピクセル数
        min_width (int): 矩形の最小幅
        min_height (int): 矩形の最小高さ
        
    Returns:
        list: [x_min, y_min, rect_width, rect_height] の形式の調整された矩形領域
    """
    # 矩形の幅と高さを計算
    rect_width = x_max - x_min + 1
    rect_height = y_max - y_min + 1
    
    # 中心座標を計算
    center_x = (x_min + x_max) // 2
    center_y = (y_min + y_max) // 2
    
    # padding適用
    if padding > 0:
        rect_width += padding * 2
        rect_height += padding * 2
    
    # 最小幅・高さ制約適用
    if rect_width < min_width:
        rect_width = min_width
    if rect_height < min_height:
        rect_height = min_height
    
    # 中心座標から新しい範囲を計算
    x_min = max(0, center_x - rect_width // 2)
    y_min = max(0, center_y - rect_height // 2)
    x_max = min(width - 1, x_min + rect_width - 1)
    y_max = min(height - 1, y_min + rect_height - 1)
    
    # 範囲を再調整（境界チェック後）
    rect_width = x_max - x_min + 1
    rect_height = y_max - y_min + 1
    
    return [int(x_min), int(y_min), int(rect_width), int(rect_height)]



def create_rectangle_mask(height, width, x, y, rect_width, rect_height):
    """
    指定した座標と大きさの矩形マスクを作成
    
    Args:
        height (int): 出力マスクの高さ
        width (int): 出力マスクの幅
        x (int): 矩形の左上X座標
        y (int): 矩形の左上Y座標
        rect_width (int): 矩形の幅
        rect_height (int): 矩形の高さ
        
    Returns:
        torch.Tensor: 矩形マスク [height, width]
    """
    mask = torch.zeros((height, width), dtype=torch.float32)
    
    # 座標が範囲内に収まるように調整
    x_end = min(width, x + rect_width)
    y_end = min(height, y + rect_height)
    x = max(0, x)
    y = max(0, y)
    
    # 矩形領域を1.0（完全不透明）に設定
    if x < x_end and y < y_end:
        mask[y:y_end, x:x_end] = 1.0
    
    return mask



def create_rectangle_from_mask(mask_np, width, height, padding=0, min_width=0, min_height=0):
    """
    マスクから矩形領域を作成する
    
    Args:
        mask_np (numpy.ndarray): マスクのNumPy配列
        width (int): 画像の幅
        height (int): 画像の高さ
        padding (int): マスクエリアを拡張するピクセル数
        min_width (int): マスクサイズの最小幅
        min_height (int): マスクサイズの最小高さ
        
    Returns:
        list: [x_min, y_min, rect_width, rect_height] の形式の矩形領域
    """
    # マスクのある範囲を取得（非ゼロの部分）
    non_zero_indices = np.nonzero(mask_np)
    
    if len(non_zero_indices[0]) == 0:
        # マスクが空の場合、全体を範囲とする
        print("Empty mask detected, using full image dimensions")
        return [0, 0, width, height]
    
    # マスクからRectangle作成
    y_min, y_max = non_zero_indices[0].min(), non_zero_indices[0].max()
    x_min, x_max = non_zero_indices[1].min(), non_zero_indices[1].max()
    
    # 矩形の寸法を調整
    return adjust_rectangle_dimensions(
        x_min, y_min, x_max, y_max, 
        width, height, 
        padding, min_width, min_height
    )





# 矩形領域の定数
MIN_RECT_DIMENSION = 10
BORDER_MARGIN = 11  # MIN_RECT_DIMENSION + 1

def validate_rectangle(rect, center_x, center_y, width, height, min_width=0, min_height=0):
    """
    矩形領域が有効かどうか確認し、無効な場合は調整する
    
    Args:
        rect (list): [x_min, y_min, rect_width, rect_height] の形式の矩形領域
        center_x (int): マスクの中心X座標
        center_y (int): マスクの中心Y座標
        width (int): 画像の幅
        height (int): 画像の高さ
        min_width (int): 最小幅
        min_height (int): 最小高さ
        
    Returns:
        list: 調整された矩形領域
    """
    x_min, y_min, rect_width, rect_height = rect
    
    # 範囲が有効かどうか確認
    if rect_width <= 0 or rect_height <= 0:
        print("Invalid rectangle dimensions, using minimal dimensions")
        x_min = min(center_x, width - BORDER_MARGIN)
        y_min = min(center_y, height - BORDER_MARGIN)
        rect_width = max(MIN_RECT_DIMENSION, min_width)
        rect_height = max(MIN_RECT_DIMENSION, min_height)
        x_max = min(width - 1, x_min + rect_width - 1)
        y_max = min(height - 1, y_min + rect_height - 1)
        rect_width = x_max - x_min + 1
        rect_height = y_max - y_min + 1
    
    return [int(x_min), int(y_min), int(rect_width), int(rect_height)]
