from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.config import MAX_UPLOAD_SIZE
from backend.models.chat import Chat
from backend.models.chat_message import ChatMessage
from backend.models.document import Document
from backend.models.user import User
from backend.services.chat.storage import upload_file


async def load_chat(chat_id: UUID, user: User, db: AsyncSession):
    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.documents), selectinload(Chat.messages))
    )
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

async def load_chat_meta(chat_id: UUID, user: User, db: AsyncSession):
    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.documents))
    )
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

async def get_recent_messages(chat_id: UUID, db: AsyncSession, limit: int):
    result = await db.scalars(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    return list(reversed(result.all()))


async def save_document(file: UploadFile, chat_id: UUID, db: AsyncSession) -> Document:
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
