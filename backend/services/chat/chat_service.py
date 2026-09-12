from backend.models.chat import Chat
from backend.models.chat_message import ChatMessage

async def load_chat(chat_id, user, db):
    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.documents), selectinload(Chat.messages))
    )
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

async def load_chat_meta(chat_id, user, db):
    chat = await db.scalar(
        select(Chat)
        .where(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.documents))
    )
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

async def get_recent_messages(chat_id, db, limit):
    result = await db.scalars(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    return list(reversed(result.all()))
