from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from backend.models.chat_message import MessageRole

class MessageResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    chat_id: UUID
    role: MessageRole
    content: str
    created_at: datetime

class MessageRequestSchema(BaseModel):
    chat_id: UUID | None = None
    content: str = Field(min_length=1, max_length=10000)

class ChatResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    messages: list[MessageResponseSchema]
    created_at: datetime

class ShortChatResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    created_at: datetime