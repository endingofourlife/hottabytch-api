from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def get_user_by_id(self, user_id: int) -> UserModel or None:
        query = (
            select(UserModel)
            .where(UserModel.user_id == user_id)
            .options(selectinload(UserModel.active_language)))
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def create_user(self, user_id: int, first_name: str, timezone: str or None) -> UserModel:
        try:
            new_user = UserModel(
                user_id=user_id,
                first_name=first_name,
                timezone=timezone
            )
            self.db_session.add(new_user)
            await self.db_session.commit()
            await self.db_session.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def update_active_language(self, user_id: int, language_id: int) -> None:
        try:
            await self.db_session.execute(
                update(UserModel)
                .where(UserModel.user_id == user_id)
                .values(active_language_id=language_id)
            )
            await self.db_session.commit()
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def reset_streak(self, user_id: int):
        try:
            await self.db_session.execute(
                update(UserModel)
                .where(UserModel.user_id == user_id)
                .values(streak=0)
            )
            await self.db_session.commit()
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e
