from fastapi import APIRouter, Depends, HTTPException, status
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
from backend.api.controllers.stubs import LLM_response

router = APIRouter(prefix="/api/chats", tags=["chats"])

@router.post("/messages", response_model=list[MessageResponseSchema], status_code=status.HTTP_201_CREATED)
async def send_message(
    message: MessageRequestSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if message.chat_id is None:
        chat = Chat(title="Unnamed Chat", user_id=user.id)
        db.add(chat)
        await db.flush()
    else:
        chat = await db.scalar(
            select(Chat).where(
                Chat.id == message.chat_id,
                Chat.user_id == user.id,
            )
        )
        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

    response = LLM_response()

    user_message = ChatMessage(role=MessageRole.user, chat_id=chat.id, content=message.content)
    ai_message = ChatMessage(role=MessageRole.assistant, chat_id=chat.id, content=response)

    db.add_all([user_message, ai_message])
    await db.commit()
    await db.refresh(user_message)
    await db.refresh(ai_message)

    return [user_message, ai_message]


@router.get("/{chat_id}", response_model=ChatResponseSchema, status_code=status.HTTP_200_OK)
async def get_chat(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.messages))
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