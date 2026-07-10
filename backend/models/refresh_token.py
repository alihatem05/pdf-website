# models.py
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Boolean, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )

    token_hash: Mapped[str] = mapped_column(
        String, 
        nullable=False, 
        unique=True, 
        index=True
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean, 
        default=False
    )

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")