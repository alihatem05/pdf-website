from pathlib import Path
from backend.config import MAX_UPLOAD_SIZE

UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "uploads"

async def upload_file(file: UploadFile, document_id):
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    filename = f"{document_id}.pdf"
    destination = UPLOAD_ROOT / filename

    contents = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(contents) > MAX_UPLOAD_SIZE:
        raise ValueError("File exceeds the upload limit")

    destination.write_bytes(contents)
    return str(destination)

def delete_file(storage_path):
    path = Path(storage_path)
    if path.exists():
        path.unlink()
