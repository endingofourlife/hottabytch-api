from contextlib import asynccontextmanager
from fastapi import FastAPI

from .redis_connection import ping_redis_server, flush_redis_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ping_redis_server()
    await flush_redis_cache()
    yield