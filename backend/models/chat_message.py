from uuid import UUID
from sqlalchemy import ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base import Base
import enum

class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))

    content: Mapped[str] = mapped_column(Text)

    chat_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chat: Mapped["Chat"] = relationship(back_populates="messages")