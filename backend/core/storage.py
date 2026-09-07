import uuid
from pathlib import Path
from fastapi import UploadFile

UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "uploads"

async def upload_file(file: UploadFile, chat_id):
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    filename = f"{chat_id}.pdf"
    destination = UPLOAD_ROOT / filename

    contents = await file.read()
    destination.write_bytes(contents)

    return str(destination)


def delete_file(storage_path):
    path = Path(storage_path)
    if path.exists():
        path.unlink()