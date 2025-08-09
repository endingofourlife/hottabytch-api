from src.database.models import UserModel
from src.schemas import UserAuthResponse
from src.schemas.user_schemas import UserBase, ActiveLanguage


class UserMapper:
    @staticmethod
    def to_user_auth_response(user: UserModel, is_streak: bool) -> UserAuthResponse:
        active_language = None
        if user.active_language:
            active_language = ActiveLanguage(
                language_id=user.active_language.language_id,
                name=user.active_language.name
            )

        return UserAuthResponse(
            user=UserBase(
                user_id=user.user_id,
                first_name=user.first_name,
                username=user.username,
                streak=user.streak,
                xp=user.xp,
                active_language=active_language,
                timezone=user.timezone,
                is_streak=is_streak
            )
        )

    @staticmethod
    def to_user_cache_auth_response(user: dict) -> UserAuthResponse:
        active_language = None
        active_language_id = user.get('active_language_id', None)
        if active_language_id:
            active_language = ActiveLanguage(
                language_id=user.get('active_language_id'),
                name=user.get('active_language_name')
            )

        return UserAuthResponse(
            user=UserBase(
                user_id=user['user_id'],
                first_name=user['first_name'],
                username=user['username'],
                streak=user['streak'],
                xp=user['xp'],
                active_language=active_language,
                timezone=user['timezone'],
                is_streak=user.get('is_streak', False)
            )
        )