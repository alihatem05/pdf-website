from uuid import UUID
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.config import MAX_UPLOAD_SIZE
from backend.core.storage import upload_file
from backend.models.chat import Chat
from backend.models.document import Document
from backend.models.user import User


async def load_chat(chat_id: UUID, user: User, db: AsyncSession) -> Chat:
    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.documents), selectinload(Chat.messages))
    )
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


async def refresh_chat(chat_id: UUID, db: AsyncSession) -> Chat:
    return await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id)
        .options(selectinload(Chat.documents), selectinload(Chat.messages))
    )


async def save_document(file: UploadFile, chat_id: UUID, db: AsyncSession) -> Document:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    document = Document(
        chat_id=chat_id,
        filename=file.filename or "document.pdf",
        storage_path="",
        status="processing",
    )
    db.add(document)
    await db.flush()
    try:
        document.storage_path = await upload_file(file, document.id, MAX_UPLOAD_SIZE)
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    return document
