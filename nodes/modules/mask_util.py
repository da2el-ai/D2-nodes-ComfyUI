import torch
from PIL import Image, ImageOps, ImageSequence, ImageFile
import numpy as np
from scipy.ndimage import gaussian_filter
from . import image_util


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



def alpha_blend_paste(img_base_rgba, img_paste_rgba, alpha_mask, x, y):
    """
    共通のアルファブレンディング処理

    Args:
        img_base_rgba (torch.Tensor): ベース画像 (RGBA) [H, W, 4]
        img_paste_rgba (torch.Tensor): 貼り付け画像 (RGBA) [pH, pW, 4]
        alpha_mask (torch.Tensor): 貼り付けに使用するアルファマスク [pH, pW] or [pH, pW, 1]
                                    (フェザリング適用済み想定)
        x (int): 貼り付け先のX座標
        y (int): 貼り付け先のY座標

    Returns:
        torch.Tensor: 合成後の画像 (RGBA) [H, W, 4]
    """
    base_height, base_width = img_base_rgba.shape[:2]
    paste_height, paste_width = img_paste_rgba.shape[:2]
    output_img = img_base_rgba.clone() # クローンを作成して直接変更

    # 貼り付け先の範囲を計算（ベース画像の範囲内に収める）
    target_y_start = max(0, y)
    target_y_end = min(base_height, y + paste_height)
    target_x_start = max(0, x)
    target_x_end = min(base_width, x + paste_width)

    # 貼り付け元（img_paste_rgba と alpha_mask）の範囲を計算
    source_y_start = target_y_start - y
    source_y_end = target_y_end - y
    source_x_start = target_x_start - x
    source_x_end = target_x_end - x

    # 実際の貼り付けサイズ
    paste_actual_height = target_y_end - target_y_start
    paste_actual_width = target_x_end - target_x_start

    if paste_actual_height > 0 and paste_actual_width > 0:
        # 関連するスライスを取得
        target_slice = output_img[target_y_start:target_y_end, target_x_start:target_x_end, :]
        source_slice = img_paste_rgba[source_y_start:source_y_end, source_x_start:source_x_end, :]

        # alpha_mask は 2D (H, W) または 3D (H, W, 1) を想定
        if alpha_mask.dim() == 2:
            mask_slice = alpha_mask[source_y_start:source_y_end, source_x_start:source_x_end].unsqueeze(-1)
        elif alpha_mask.dim() == 3:
            mask_slice = alpha_mask[source_y_start:source_y_end, source_x_start:source_x_end, :]
        else:
            raise ValueError(f"Unexpected alpha_mask dimension: {alpha_mask.dim()}")

        # アルファチャンネルを計算 (貼り付け画像のアルファ * マスク)
        # source_sliceをRGBAに変換 (必要な場合)
        source_slice_rgba = image_util.convert_to_rgba_or_rgb(source_slice, "rgba")

        alpha = source_slice_rgba[:, :, 3:4] * mask_slice

        # アルファブレンディング
        target_slice[:, :, :3] = target_slice[:, :, :3] * (1 - alpha) + source_slice_rgba[:, :, :3] * alpha

        # アルファチャンネルを更新 (ベースのアルファと貼り付けアルファを加算、最大1にクランプ)
        target_slice[:, :, 3:4] = torch.clamp(target_slice[:, :, 3:4] + alpha, 0, 1)

        # 結果を書き戻し (クローンなので不要、直接変更されている)
        # output_img[target_y_start:target_y_end, target_x_start:target_x_end, :] = target_slice
    else:
        print(f"alpha_blend_paste: Warning - Paste area is outside the base image bounds or has zero size ({paste_actual_width}x{paste_actual_height}).")

    return output_img



def adjust_rectangle_dimensions(rect, width, height, padding=0, min_width=0, min_height=0):
    """
    矩形領域の寸法を調整する
    
    Args:
        rect (list): [x, y, width, height]
        width (int): 画像の幅
        height (int): 画像の高さ
        padding (int): 矩形を拡張するピクセル数
        min_width (int): 矩形の最小幅
        min_height (int): 矩形の最小高さ
        
    Returns:
        list: [x_min, y_min, rect_width, rect_height] の形式の調整された矩形領域
    """
    # 矩形の幅と高さを計算
    x_min = rect[0]
    y_min = rect[1]
    rect_width = rect[2]
    rect_height = rect[3]
    # print(f"Debug - adjust_rectangle_dimensions()1: x_min={x_min}, y_min={y_min}, rect_width={rect_width}, rect_height={rect_height}")

    # 中心座標を計算
    center_x = x_min + rect_width // 2
    center_y = y_min + rect_height // 2
    
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
    
    # print(f"Debug - adjust_rectangle_dimensions()2: x_min={x_min}, y_min={y_min}, rect_width={rect_width}, rect_height={rect_height}")
    return [int(x_min), int(y_min), int(rect_width), int(rect_height)]


def adjust_rectangle_to_area(rect, area_width, area_height):
    """
    矩形がエリア内に収まるように調整する関数
    
    サイズを優先し、座標を調整する。
    エリアをはみ出る場合は切り落とす。
    
    Args:
        rect (list): [x, y, width, height]
        area_width (int): エリアの幅
        area_height (int): エリアの高さ
        
    Returns:
        list: [x, y, width, height] の形式の調整された矩形
    """
    rect_x = rect[0]
    rect_y = rect[1]
    rect_width = rect[2]
    rect_height = rect[3]
    # print(f"Debug - adjust_rectangle_to_area(): rect_x={rect_x}, rect_y={rect_y}, rect_width={rect_width}, rect_height={rect_height}, area_width={area_width}, area_height={area_height}")

    # まずサイズの調整（エリアサイズを超えないように）
    adjusted_width = min(rect_width, area_width)
    adjusted_height = min(rect_height, area_height)
    
    # 座標の調整（矩形全体がエリア内に入るように）
    # 右端/下端がエリアを超える場合、左上の座標を調整
    if rect_x + adjusted_width > area_width:
        adjusted_x = max(0, area_width - adjusted_width)
    else:
        adjusted_x = max(0, rect_x)
        
    if rect_y + adjusted_height > area_height:
        adjusted_y = max(0, area_height - adjusted_height)
    else:
        adjusted_y = max(0, rect_y)
    
    # print(f"Debug - adjust_rectangle_to_area(): adjusted_x={adjusted_x}, adjusted_y={adjusted_y}, adjusted_width={adjusted_width}, adjusted_height={adjusted_height}")
    
    return [int(adjusted_x), int(adjusted_y), int(adjusted_width), int(adjusted_height)]


def create_rectangle_mask(height, width, x, y, rect_width, rect_height, alpha=1.0):
    """
    指定した座標と大きさの矩形マスクを作成
    
    Args:
        height (int): 出力マスクの高さ
        width (int): 出力マスクの幅
        x (int): 矩形の左上X座標
        y (int): 矩形の左上Y座標
        rect_width (int): 矩形の幅
        rect_height (int): 矩形の高さ
        alpha (float): マスクの不透明度（初期値 1.0）
        
    Returns:
        torch.Tensor: 矩形マスク [height, width]
    """
    mask = torch.zeros((height, width), dtype=torch.float32)
    
    # 座標が範囲内に収まるように調整
    x_end = min(width, x + rect_width)
    y_end = min(height, y + rect_height)
    x = max(0, x)
    y = max(0, y)
    
    # 矩形領域を指定された不透明度に設定
    if x < x_end and y < y_end:
        mask[y:y_end, x:x_end] = alpha
    
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
    # print(f"Debug - create_rectangle_from_mask()1: x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}")
    
    rect = [
        x_min, 
        y_min, 
        x_max - x_min + 1, 
        y_max - y_min + 1
    ]
    # print(f"Debug - create_rectangle_from_mask()2: rect={rect}")
    
    # 矩形の寸法を調整
    return adjust_rectangle_dimensions(
        rect,
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

