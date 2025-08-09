from environs import Env
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

env = Env()
env.read_env('.env')

DATABASE_URL = "sqlite+aiosqlite:///database.db" # for testing purposes  TODO: REMOVE AIOSQLITE!!!!

engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
