"""merge chat schema heads

Revision ID: c8d9e0f1a2b3
Revises: 6e25ec79d56a, a4c7e9f1b2d3
Create Date: 2026-09-13

"""
from typing import Sequence, Union


revision: str = "c8d9e0f1a2b3"
down_revision: Union[str, Sequence[str], None] = ("6e25ec79d56a", "a4c7e9f1b2d3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
