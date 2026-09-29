from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Text, Enum, case
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base import Base
import enum

if TYPE_CHECKING:
    from .chat import Chat


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


def message_ordering(descending=False):
    role_order = case(
        (ChatMessage.role == MessageRole.user, 0),
        (ChatMessage.role == MessageRole.assistant, 1),
        else_=2,
    )
    if descending:
        return ChatMessage.created_at.desc(), role_order.desc()
    return ChatMessage.created_at.asc(), role_order.asc()