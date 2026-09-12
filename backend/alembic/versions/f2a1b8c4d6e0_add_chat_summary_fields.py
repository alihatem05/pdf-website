"""add chat summary fields

Revision ID: f2a1b8c4d6e0
Revises: e7d2cb22bfc7
Create Date: 2026-09-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a1b8c4d6e0"
down_revision: Union[str, Sequence[str], None] = "e7d2cb22bfc7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chats", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("chats", sa.Column("summarized_up_to", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("chats", "summarized_up_to", server_default=None)


def downgrade() -> None:
    op.drop_column("chats", "summarized_up_to")
    op.drop_column("chats", "summary")
