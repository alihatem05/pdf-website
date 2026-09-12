import uuid
from pathlib import Path
from fastapi import UploadFile

UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "uploads"

async def upload_file(file: UploadFile, document_id, max_size=None):
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    filename = f"{document_id}.pdf"
    destination = UPLOAD_ROOT / filename

    contents = await file.read(max_size + 1) if max_size is not None else await file.read()
    if max_size is not None and len(contents) > max_size:
        raise ValueError("File exceeds the upload limit")
    destination.write_bytes(contents)

    return str(destination)


def delete_file(storage_path):
    path = Path(storage_path)
    if path.exists():
        path.unlink()