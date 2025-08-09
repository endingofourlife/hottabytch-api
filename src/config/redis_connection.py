from redis import asyncio as aioredis
import logging
from dotenv import load_dotenv
import os

load_dotenv()
HOST = os.getenv('REDIS_HOST')
PORT = int(os.getenv('REDIS_PORT'))
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

logger = logging.getLogger('redis_connection')
redis_client = aioredis.Redis(
    host=HOST,
    port=PORT,
    decode_responses=True,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
)

async def ping_redis_server():
    try:
        await redis_client.ping()
        logger.info("Redis server is reachable")
    except Exception as e:
        logger.error(f"Error connecting to Redis server: {e}")
        raise ConnectionError("Could not connect to Redis server") from e

def get_redis_client() -> aioredis.Redis:
    """
    Returns the Redis client instance.
    """
    return redis_client