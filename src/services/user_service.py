import json
import logging
from datetime import datetime

import pytz
from redis.asyncio import Redis

from src.repository import UserRepository, PLanguageRepository
from src.schemas import UserAuthRequest, LanguageUpdateRequest, LanguageUpdateResponse
from .mappers import UserMapper
from .service_result import ServiceResult
from ..database.models import UserModel

logger = logging.getLogger('user_service')

class UserService:
    def __init__(self, repository: UserRepository, language_repo: PLanguageRepository, redis_client: Redis):
        self._repository = repository
        self._language_repo = language_repo
        self._redis_client = redis_client

    async def _is_streak_active(self, user: UserModel) -> bool:
        if not user.last_lesson_date:
            return False
        user_tz = user.timezone
        try:
            tz = pytz.timezone(user_tz)
            today = datetime.now(tz).date()
            last_lesson_date = user.last_lesson_date.astimezone(tz).date()
            delta = (today - last_lesson_date).days
            if delta > 1 and user.streak > 0:
                logger.debug(f"Streak inactive for user {user.user_id}: last lesson was {delta} days ago")
                await self._repository.reset_streak(user.user_id)
                await self._redis_client.delete(f'user:{user.user_id}')
                return False
            return delta == 0
        except pytz.exceptions.UnknownTimeZoneError as e:
            logger.error(f"Unknown timezone {user_tz} for user {user.user_id}: {e}")
            raise ValueError(f"Unknown timezone {user_tz} for user {user.user_id}")

    def _cache_user(self, user: UserModel, is_streak: bool):
        cache_key = f'user:{user.user_id}'
        user_data = {
            'user_id': user.user_id,
            'first_name': user.first_name,
            'username': user.username,
            'streak': user.streak,
            'xp': user.xp,
            'timezone': user.timezone,
            'is_streak': is_streak,
            'active_language_id': user.active_language_id if user.active_language_id else None,
            'active_language_name': user.active_language.name if user.active_language else None,
        }
        return self._redis_client.setex(
            cache_key,
            time=3600,
            value=json.dumps(user_data)
        )

    async def _get_cached_user(self, user_id: int) -> dict | None:
        cache_key = f'user:{user_id}'
        cached_user = await self._redis_client.get(cache_key)
        if cached_user:
            logger.debug(f"User {user_id} found in cache")
            return json.loads(cached_user)
        logger.debug(f"User {user_id} not found in cache")
        return None

    async def get_user_by_id(self, user_id: int) -> ServiceResult:
        try:
            await self._redis_client.delete(f'user:{user_id}')
            logger.debug(f"Checking cache for user with ID: {user_id}")
            cached_user = await self._get_cached_user(user_id)
            if cached_user:
                logger.info(f"User {user_id} found in cache")
                return ServiceResult.success(UserMapper.to_user_cache_auth_response(cached_user))

            logger.debug(f"Fetching user with ID: {user_id}")
            user = await self._repository.get_user_by_id(user_id)
            if not user:
                logger.info(f"User with ID {user_id} not found")
                return ServiceResult.failure(f'User with ID {user_id} not found', status_code=404)

            logger.debug(f"User found: {user}")
            is_streak = await self._is_streak_active(user)

            logger.debug(f"User {user_id} streak status: {is_streak}")
            await self._cache_user(user, is_streak)
            logger.info(f"User {user_id} cached successfully")

            return ServiceResult.success(UserMapper.to_user_auth_response(user, is_streak))

        except Exception as e:
            logger.error(f"Error fetching user with ID {user_id}: {e}")
            return ServiceResult.failure('Error fetching user', status_code=500)

    async def auth_user(self, request: UserAuthRequest) -> ServiceResult:
        logger.debug('Authenticating user with request: %s', request)

        user_result = await self.get_user_by_id(request.user_id)
        if user_result.is_success:
            logger.debug(f"User with ID {request.user_id} found")
            return user_result

        if user_result.status_code == 500:
            logger.error(f"Error fetching user with ID {request.user_id}: {user_result.error}")
            return ServiceResult.failure('Error fetching user: ' + user_result.error, status_code=500)

        logger.debug(f"User with ID {request.user_id} not found. Creating a new user.")

        try:
            new_user = await self._repository.create_user(
                user_id=request.user_id,
                first_name=request.first_name,
                username=request.username,
                timezone= request.timezone
            )
            logger.info(f"New user created: {new_user.user_id}")
            return ServiceResult.success(UserMapper.to_user_auth_response(new_user, False))
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return ServiceResult.failure('Error creating user: ' + str(e))

    async def set_active_language(self, user_id:int, request: LanguageUpdateRequest):
        logger.debug(f"Setting active language for user ID {user_id} to language ID {request.language_id}")
        try:
            language = await self._language_repo.get_language_by_id(request.language_id)
            if not language:
                logger.warning(f"Language with ID {request.language_id} not found")
                return ServiceResult.failure(f'Language with ID {request.language_id} not found', status_code=404)

            user = await self._repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User with ID {user_id} not found")
                return ServiceResult.failure(f'User with ID {user_id} not found', status_code=404)

            await self._repository.update_active_language(
                user_id=user.user_id,
                language_id=language.language_id
            )
            logger.info(f"Active language updated for user ID {user_id}")

            # Invalidate the cache for the user
            await self._redis_client.delete(f'user:{user_id}')
            logger.debug(f"Cache for user {user_id} invalidated")

            return ServiceResult.success(
                LanguageUpdateResponse(
                    success=True
                )
            )
        except ValueError as ve:
            logger.warning(f"Value error: {ve}")
            return ServiceResult.failure('Error setting active language' + str(ve), status_code=404)
        except Exception as e:
            logger.error(f"Error updating active language: {e}")
            return ServiceResult.failure('Error updating active language: ' + str(e), status_code=500)
