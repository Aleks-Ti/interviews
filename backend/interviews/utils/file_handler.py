import logging
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

logger = logging.getLogger(__name__)


async def handle_file_upload(file: UploadFile | None, dir_name: str) -> str | None:
    if file is None:
        return None
    try:
        ext = Path(file.filename).suffix.lower()
        file_dir = Path("static") / dir_name
        file_dir.mkdir(parents=True, exist_ok=True)
        content = await file.read()
        file_name = f"{uuid.uuid4().hex}{ext}"
        async with aiofiles.open(Path(file_dir, file_name), "wb") as buffer:
            await buffer.write(content)
        return str(file_dir / file_name)
    except Exception as err:
        if locals().get("file_dir") and locals().get("file_name"):
            logging.exception(f"Error while uploading file. File_dir: {file_dir} File_name: {file_name} Error: {err}")
        else:
            logging.exception(f"Error while uploading file. Error: {err}")
        return None

def handle_file_delete(file_path: str | None):
    try:
        path_to_file = Path(file_path)
        if path_to_file.exists():
            path_to_file.unlink(missing_ok=True)
    except Exception as err:
        logging.exception(f"Error while deleting file. File_path: {file_path} Error: {err}")
