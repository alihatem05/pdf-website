from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .base import Base

if TYPE_CHECKING:
    from .chat_message import ChatMessage
    from .document import Document
    from .user import User


class Chat(Base):
    __tablename__ = "chats"

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Chat",
    )

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    summarized_up_to: Mapped[int] = mapped_column(default=0, nullable=False)
    message_count: Mapped[int] = mapped_column(default=0, nullable=False)

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="chats")

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
    )

