from logging.config import fileConfig
import sys
from pathlib import Path

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import DATABASE_URL
from models.base import Base
from models.user import User
from models.refresh_token import RefreshToken

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your backend/.env file.")


def run_migrations_offline() -> None:
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async def do_run_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(lambda sync_conn: context.configure(connection=sync_conn, target_metadata=target_metadata))

            async with connection.begin():
                await connection.run_sync(lambda sync_conn: context.run_migrations())

    import asyncio
    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
