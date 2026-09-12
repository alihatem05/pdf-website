from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from backend.schemas.chat import (ChatResponseSchema, MessageResponseSchema, ShortChatResponseSchema, MessageRequestSchema)
from backend.database import get_db
from backend.models.chat import Chat
from backend.dependencies.auth import get_current_user
from backend.models.user import User
from backend.models.chat_message import ChatMessage, MessageRole
from backend.services.chat.storage import delete_file
from backend.config import CHAT_HISTORY_LIMIT, SUMMARY_THRESHOLD
from backend.services.chat.chat_service import get_recent_messages, load_chat, load_chat_meta, save_document
from backend.services.llm.embed import embed_file, delete_embedding
from backend.services.llm.graph import rag_graph
from backend.services.llm.client import get_messages
from backend.services.llm.summarize import update_chat_summary

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.post("/messages", response_model=list[MessageResponseSchema], status_code=status.HTTP_201_CREATED)
async def send_message(
    message: MessageRequestSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await load_chat_meta(message.chat_id, user, db)
    recent_messages = await get_recent_messages(chat.id, db, CHAT_HISTORY_LIMIT)
    history = get_messages(recent_messages)
    result = await rag_graph.ainvoke({
        "chat_id": chat.id,
        "question": message.content,
        "history": history,
        "summary": chat.summary,
    })

    user_message = ChatMessage(role=MessageRole.user, chat_id=chat.id, content=message.content)

    ai_message = ChatMessage(role=MessageRole.assistant, chat_id=chat.id, content=result["answer"])

    db.add_all([user_message, ai_message])
    chat.message_count += 2
    await db.commit()
    await db.refresh(user_message)
    await db.refresh(ai_message)

    if chat.message_count - chat.summarized_up_to >= SUMMARY_THRESHOLD:
        update_chat_summary.delay(str(chat.id))

    return [user_message, ai_message]


@router.post("/documents", response_model=ChatResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_chat_with_document(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one PDF file is required",
        )

    if any(file.content_type != "application/pdf" for file in files):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    chat = Chat(title=files[0].filename or "New Chat", user_id=user.id)
    db.add(chat)
    await db.flush()

    documents = [await save_document(file, chat.id, db) for file in files]
    await db.commit()

    chat = await load_chat(chat.id, user, db)

    for document in documents:
        embed_file.delay(str(document.id), str(chat.id))

    return chat


@router.get("/{chat_id}", response_model=ChatResponseSchema, status_code=status.HTTP_200_OK)
async def get_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await load_chat(chat_id, user, db)


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
    chat = await load_chat_meta(chat_id, user, db)

    for document in chat.documents:
        delete_file(document.storage_path)
    if chat.documents:
        delete_embedding(chat.id)

    await db.delete(chat)
    await db.commit()

    return {"message": "Chat deleted successfully"}