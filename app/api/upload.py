from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
from app.core.auth import verify_admin

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("app/static/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/image")
async def upload_image(
        file: UploadFile = File(...),
        admin: str = Depends(verify_admin)
):
    """Загрузка изображения для вопроса"""
    # Проверяем тип файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Генерируем уникальное имя
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Сохраняем файл
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Возвращаем URL для доступа к файлу
    file_url = f"/static/images/{unique_filename}"
    return {"url": file_url, "filename": unique_filename}