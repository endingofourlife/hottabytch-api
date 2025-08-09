from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db, get_redis_client
from src.core import handle_service_result
from src.repository import UserRepository, PLanguageRepository
from src.schemas import UserAuthRequest, UserAuthResponse, LanguageUpdateRequest, LanguageUpdateResponse
from src.services import UserService, ServiceResult

user_router = APIRouter()

async def get_user_service(
        session: AsyncSession = Depends(get_db),
        redis_client: Redis = Depends(get_redis_client)
) -> UserService:
    return UserService(UserRepository(session), PLanguageRepository(session), redis_client)

@user_router.post('/auth', summary='Authenticate user via Telegram', response_model=UserAuthResponse)
async def authenticate_user(request: UserAuthRequest, service: UserService = Depends(get_user_service)):
    response = await service.auth_user(request)
    return handle_service_result(response)

@user_router.patch('/{user_id}/change-language', summary='Set active programming language for user', response_model=LanguageUpdateResponse)
async def update_active_language(user_id: int, request: LanguageUpdateRequest, service: UserService = Depends(get_user_service)):
    response = await service.set_active_language(user_id, request)
    return handle_service_result(response)

