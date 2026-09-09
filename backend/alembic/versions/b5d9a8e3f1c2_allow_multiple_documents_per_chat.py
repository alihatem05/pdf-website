"""allow multiple PDF documents per chat"""

from alembic import op


revision = "b5d9a8e3f1c2"
down_revision = "7ad66bdd1253"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("documents_chat_id_key", "documents", type_="unique")
    op.create_index("ix_documents_chat_id", "documents", ["chat_id"])


def downgrade() -> None:
    op.drop_index("ix_documents_chat_id", table_name="documents")
    op.create_unique_constraint("documents_chat_id_key", "documents", ["chat_id"])