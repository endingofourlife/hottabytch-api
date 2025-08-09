from contextlib import asynccontextmanager
from fastapi import FastAPI

from .redis_connection import ping_redis_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_redis_server()
    yield