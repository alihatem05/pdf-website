"""add chat message count

Revision ID: a4c7e9f1b2d3
Revises: f2a1b8c4d6e0
Create Date: 2026-09-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4c7e9f1b2d3"
down_revision: Union[str, Sequence[str], None] = "f2a1b8c4d6e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chats", sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("chats", "message_count", server_default=None)


def downgrade() -> None:
    op.drop_column("chats", "message_count")