from dataclasses import dataclass
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
# from .util import pil2tensor, tensor2pil


FONT_PATH = str(Path(__file__).parent.parent.parent / "static" / "Roboto-Regular.ttf")
PADDING = 16

@dataclass
class GridData:
    image: Image.Image
    size: tuple[int, int]
    gap: int
    columns: int
    rows: int


"""

見出しテキストの作成用データ

"""
class AnnotationData:
    column_texts: list[str]
    row_texts: list[str]
    font: ImageFont.FreeTypeFont

    def __init__(self, column_texts, row_texts, font_size):
        self.column_texts = column_texts
        self.row_texts = row_texts
        self.font = ImageFont.truetype(FONT_PATH, size = font_size)

"""

文字画像を作成

"""
def _get_text_image(
    annotation_data: AnnotationData,
    text: str
) -> Image.Image:
    
    # 仮のImageを作成してテキストサイズを計算
    temp_draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    text_width = temp_draw.textlength(text, font=annotation_data.font)
    text_height = annotation_data.font.size
    
    # 画像を作成
    text_image = Image.new('RGB', (int(text_width), text_height), color=0xffffff)
    draw = ImageDraw.Draw(text_image)
    
    # テキストを描画（左揃え）
    draw.text(
        (0, 0),
        text,
        font=annotation_data.font,
        fill=(0, 0, 0)  # 黒色
    )
    return text_image

"""

column 画像を作成

"""
def _create_column_image(
    grid_data: GridData,
    annotation_data: AnnotationData
) -> Image.Image:
    column_images = []
    column_height = 0

    for text in annotation_data.column_texts:
        img = _get_text_image(annotation_data, text)
        column_height = max(column_height, img.size[1])
        column_images.append(img)

    padding_height = column_height + (PADDING * 2)
    column_image = Image.new('RGB', (grid_data.image.size[0], padding_height), color=0xffffff)

    for i, img in enumerate(column_images):
        label = Image.new('RGB', (grid_data.size[0], padding_height), color=0xffffff)

        # テキスト画像のサイズ調整
        # アスペクト比を維持しながら縮小
        if img.size[0] > grid_data.size[0]:
            ratio = grid_data.size[0] / img.size[0]
            new_size = (grid_data.size[0], int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # label の中央に img を配置
        paste_x = (grid_data.size[0] - img.size[0]) // 2
        paste_y = (padding_height - img.size[1]) // 2
        label.paste(img, (paste_x, paste_y))

        # column_image に label を貼りつける
        x = i * (grid_data.size[0] + grid_data.gap)
        y = 0
        column_image.paste(label, (x, y))
        
    return column_image

"""

row 画像を作成

"""
def _create_row_image(
    grid_data: GridData,
    annotation_data: AnnotationData
) -> Image.Image:
    row_images = []
    row_width = 0

    for text in annotation_data.row_texts:
        img = _get_text_image(annotation_data, text)
        row_width = max(row_width, img.size[0])
        row_images.append(img)

    padding_width = row_width + (PADDING * 2)
    row_image = Image.new('RGB', (padding_width, grid_data.image.size[1]), color=0xffffff)

    for i, img in enumerate(row_images):
        label = Image.new('RGB', (padding_width, grid_data.size[0]), color=0xffffff)

        # テキスト画像のサイズ調整
        # アスペクト比を維持しながら縮小
        if img.size[1] > grid_data.size[1]:
            ratio = grid_data.size[1] / img.size[1]
            new_size = (int(img.size[0] * ratio), grid_data.size[1])
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # label の中央に img を配置
        paste_x = (padding_width - img.size[0]) // 2
        paste_y = (grid_data.size[1] - img.size[1]) // 2
        label.paste(img, (paste_x, paste_y))

        # column_image に label を貼りつける
        x = 0
        y = i * (grid_data.size[1] + grid_data.gap)
        row_image.paste(label, (x, y))

    return row_image

"""

見出しテキストを作成

"""
def _create_annotation_image(
    grid_data: GridData,
    annotation_data: AnnotationData
) -> tuple[Image.Image, int, int]:
    
    if not annotation_data.column_texts and not annotation_data.row_texts:
        raise ValueError("Column text and row text is empty")

    column_image = _create_column_image(grid_data, annotation_data)
    row_image = _create_row_image(grid_data, annotation_data)
    label_width = row_image.size[0]
    label_height = column_image.size[1]

    width = grid_data.image.size[0] + label_width
    height = grid_data.image.size[1] + label_height
    annotation_image = Image.new('RGB', (width, height), color=0xffffff)

    annotation_image.paste(column_image, (label_width, 0))
    annotation_image.paste(row_image, (0, label_height))
    return (annotation_image, label_width, label_height)

"""

横方向のグリッド画像を作成

"""
def create_grid_by_columns(
    images: list[Image.Image],
    gap: int,
    max_columns: int
) -> GridData:
    
    size = images[0].size
    max_rows = math.ceil(len(images) / max_columns)

    grid_width = size[0] * max_columns + (max_columns - 1) * gap
    grid_height = size[1] * max_rows + (max_rows - 1) * gap
    
    grid_image = Image.new("RGB", (grid_width, grid_height), color=0xffffff)

    # 画像を配置
    for i, img in enumerate(images):
        # 現在の行と列を計算
        current_row = i // max_columns
        current_col = i % max_columns
        
        # 配置位置を計算
        x = current_col * (size[0] + gap)
        y = current_row * (size[1] + gap)
        
        # 画像を配置
        grid_image.paste(img, (x, y))
    
    grid_data = GridData(
        image = grid_image,
        size = size,
        gap = gap,
        columns = max_columns,
        rows = max_rows
    )

    return grid_data

"""

縦方向のグリッド画像を作成

"""
def create_grid_by_rows(
    images: list[Image.Image],
    gap: int,
    max_rows: int
) -> GridData:
    
    size = images[0].size
    max_columns = math.ceil(len(images) / max_rows)

    grid_width = size[0] * max_columns + (max_columns - 1) * gap
    grid_height = size[1] * max_rows + (max_rows - 1) * gap
    
    grid_image = Image.new("RGB", (grid_width, grid_height), color=0xffffff)

    # 画像を配置
    for i, img in enumerate(images):
        # 現在の行と列を計算
        current_row = i % max_rows
        current_col = i // max_rows
        
        # 配置位置を計算
        x = current_col * (size[0] + gap)
        y = current_row * (size[1] + gap)
        
        # 画像を配置
        grid_image.paste(img, (x, y))
    
    grid_data = GridData(
        image = grid_image,
        size = size,
        gap = gap,
        columns = max_columns,
        rows = max_rows
    )

    return grid_data

"""

横方向グリッド画像＋見出し作成

"""
def create_grid_with_annotation_by_columns(
    images: list[Image.Image],
    gap: int,
    max_columns: int,
    column_texts: list[str],
    row_texts: list[str],
    font_size: int,
) -> Image.Image:
    
    grid_data = create_grid_by_columns(
        images = images,
        gap = gap,
        max_columns = max_columns
    )

    annotation_data = AnnotationData(
        column_texts = column_texts,
        row_texts = row_texts,
        font_size = font_size
    )

    annotation_image, label_width, label_height = _create_annotation_image(
        grid_data = grid_data,
        annotation_data = annotation_data
    )
    annotation_image.paste(grid_data.image, (label_width, label_height))
    return annotation_image

"""

縦方向グリッド画像＋見出し作成

"""
def create_grid_with_annotation_by_rows(
    images: list[Image.Image],
    gap: int,
    max_rows: int,
    column_texts: list[str],
    row_texts: list[str],
    font_size: int,
) -> Image.Image:
    
    grid_data = create_grid_by_rows(
        images = images,
        gap = gap,
        max_rows = max_rows
    )

    annotation_data = AnnotationData(
        column_texts = column_texts,
        row_texts = row_texts,
        font_size = font_size
    )

    annotation_image, label_width, label_height = _create_annotation_image(
        grid_data = grid_data,
        annotation_data = annotation_data
    )
    annotation_image.paste(grid_data.image, (label_width, label_height))
    return annotation_image


# # 画像フォルダのパス
# folder_path = "./img/"

# # フォルダ内の画像ファイルを取得
# image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

# if not image_files:
#     print("画像ファイルが見つかりません")
# else:
#     # 画像を読み込み
#     images = []
#     for file_name in image_files:
#         file_path = os.path.join(folder_path, file_name)
#         try:
#             img = Image.open(file_path)
#             images.append(img)
#         except Exception as e:
#             print(f"画像の読み込みエラー {file_name}: {e}")

#     # グリッド画像を作成
#     grid_image = create_grid_by_rows(
#         images=images,
#         gap=64,
#         max_rows=3,
#         row_texts=["aaaaaaaa", "bbbbbbb", "ccccccc"],
#         column_texts=["fdajldfjaoa;poeil;kdjfa", "BBBBBB"],
#         font_size=32
#     )

#     # grid_data = create_grid_by_rows(
#     #     images=images,
#     #     gap=64,
#     #     max_rows=3,
#     # )
#     # grid_image = grid_data.image


#     # 結果を保存
#     grid_image.save("./grid_result.png")
#     print("グリッド画像を保存しました: ./grid_result.png")