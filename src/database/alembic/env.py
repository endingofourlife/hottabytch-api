import asyncio
from logging.config import fileConfig

from environs import Env
from sqlalchemy import pool, URL
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from src.database.models import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

env = Env()
env.read_env('.env')

# url = URL.create( # for production
#     drivername='postgresql+asyncpg',
#     username=env.str('POSTGRES_USER'),
#     password=env.str('POSTGRES_PASSWORD'),
#     host=env.str('POSTGRES_HOST'),
#     database=env.str('POSTGRES_DB'),
#     port=5432
# ).render_as_string(hide_password=False)
url = "sqlite+aiosqlite:///database.db" # for testing purposes

config.set_main_option("sqlalchemy.url", str(url))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()