from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID
from backend.schemas.chat import (ChatResponseSchema, MessageResponseSchema, ShortChatResponseSchema, MessageRequestSchema)
from backend.database import get_db
from backend.models.chat import Chat
from backend.dependencies.auth import get_current_user
from backend.models.user import User
from backend.models.chat_message import ChatMessage, MessageRole
from backend.models.document import Document
from backend.services.client import llm_response, get_messages
from backend.core.storage import upload_file, delete_file
from backend.services.embed import embed_file, delete_embedding

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.post("/messages", response_model=list[MessageResponseSchema], status_code=status.HTTP_201_CREATED)
async def send_message(
    message: MessageRequestSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await db.scalar(
        select(Chat)
        .options(selectinload(Chat.messages))
        .where(
            Chat.id == message.chat_id,
            Chat.user_id == user.id,
        )
    )
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    user_message = ChatMessage(role=MessageRole.user, chat_id=chat.id, content=message.content)

    messages = get_messages(chat.messages)
    messages.append({"role": user_message.role.value, "content": user_message.content})

    response = llm_response(messages)

    ai_message = ChatMessage(role=MessageRole.assistant, chat_id=chat.id, content=response)

    db.add_all([user_message, ai_message])
    await db.commit()
    await db.refresh(user_message)
    await db.refresh(ai_message)

    return [user_message, ai_message]


@router.post("/documents", response_model=ChatResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_chat_with_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    chat = Chat(title=file.filename, user_id=user.id)
    db.add(chat)
    await db.flush()

    storage_path = await upload_file(file, chat.id)

    document = Document(
        chat_id=chat.id,
        filename=file.filename,
        storage_path=storage_path,
        status="processing",
    )
    
    db.add(document)
    await db.commit()

    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat.id)
        .options(selectinload(Chat.messages), selectinload(Chat.document))
    )

    embed_file.delay(str(document.id))

    return chat


@router.get("/{chat_id}", response_model=ChatResponseSchema, status_code=status.HTTP_200_OK)
async def get_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.messages), selectinload(Chat.document))
    )

    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat


@router.get("", response_model=list[ShortChatResponseSchema], status_code=status.HTTP_200_OK)
async def list_chats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    last_msg = (
        select(ChatMessage.chat_id, func.max(ChatMessage.created_at).label("last_at"))
        .group_by(ChatMessage.chat_id)
        .subquery()
    )

    result = await db.execute(
        select(Chat)
        .outerjoin(last_msg, last_msg.c.chat_id == Chat.id)
        .where(Chat.user_id == user.id)
        .order_by(func.coalesce(last_msg.c.last_at, Chat.created_at).desc())
    )
    return result.scalars().all()


@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await db.scalar(
        select(Chat)
        .where(
            Chat.id == chat_id,
            Chat.user_id == user.id,
        ).options(selectinload(Chat.document))
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    document = chat.document

    if document is not None:
        delete_file(document.storage_path)
        delete_embedding(chat.id)

    await db.delete(chat)
    await db.commit()

    return {"message": "Chat deleted successfully"}