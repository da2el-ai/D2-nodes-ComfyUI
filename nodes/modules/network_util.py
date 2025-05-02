import mimetypes, os, uuid
from aiohttp import web
import folder_paths

from server import PromptServer


@PromptServer.instance.routes.post("/D2/network/image/upload")
async def route_image_upload(request):
    """
    画像アップロード
    """
    try:
        # マルチパートリクエストを読み込む
        reader = await request.multipart()
        
        # アップロードされたファイルを保存するディレクトリ
        upload_dir = folder_paths.get_temp_directory()
        
        uploaded_files = []
        
        # リクエストから各ファイルを処理
        while True:
            part = await reader.next()
            if part is None:
                break
                
            # ファイル名がフィールド名に含まれているか確認
            if part.name.startswith('file'):
                # オリジナルのファイル名を取得
                filename = part.filename
                if not filename:
                    continue
                
                # MIMEタイプをチェックして画像かどうか確認
                content_type = mimetypes.guess_type(filename)[0]
                if not content_type or not content_type.startswith('image/'):
                    continue
                
                # ユニークなファイル名を生成
                # file_ext = os.path.splitext(filename)[1]
                # unique_filename = f"{uuid.uuid4()}{file_ext}"
                unique_filename = filename
                file_path = os.path.join(upload_dir, unique_filename)
                
                # ファイルを保存
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        f.write(chunk)
                
                # アップロードしたファイルの情報を追加
                uploaded_files.append({
                    "original_name": filename,
                    "saved_name": unique_filename,
                    "path": file_path,
                    # "url": f"/view/input/{unique_filename}"
                })
        
        # 結果をJSONで返す
        result = {
            "success": True,
            "message": f"{len(uploaded_files)} files uploaded successfully",
            "files": uploaded_files
        }
        return web.json_response(result)
        
    except Exception as e:
        # エラー処理
        return web.json_response({
            "success": False,
            "message": f"Error occurred during upload: {str(e)}"
        }, status=500)

