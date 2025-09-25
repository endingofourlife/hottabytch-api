from typing import Any, Coroutine, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import PLanguageModel


class PLanguageRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def get_language_by_id(self, language_id: int) -> PLanguageModel | None:
        language = await self.db_session.get(PLanguageModel, language_id)
        return language

    async def get_all_languages(self) -> Sequence[PLanguageModel]:
        query = select(PLanguageModel)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def add_language(self, name: str, description: str, picture: str, level: str, popularity: int) -> PLanguageModel:
        try:
            new_language = PLanguageModel(name=name, description=description, picture=picture, level=level, popularity=popularity)
            self.db_session.add(new_language)
            await self.db_session.commit()
            await self.db_session.refresh(new_language)
            return new_language
        except Exception as e:
            await self.db_session.rollback()
            raise e
