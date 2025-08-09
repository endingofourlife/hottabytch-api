from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import LessonModel, QuestionModel


class LessonRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def all_lessons(self) -> Sequence[LessonModel]:
        query = select(LessonModel)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_lesson_by_id(self, lesson_id: int) -> LessonModel | None:
        query = (
            select(LessonModel)
            .where(LessonModel.lesson_id == lesson_id)
            .options(selectinload(LessonModel.questions).selectinload(QuestionModel.answers))
        )
        result = await self.db_session.execute(query)
        return result.scalars().first()

    # async def add_lesson(self, title: str, description: str, language_id: int) -> LessonModel | None:
    #     try:
    #         new_lesson = LessonModel(title=title,
    #                                  description=description,
    #                                  language_id=language_id,
    #                                  questions=[])
    #         self.db_session.add(new_lesson)
    #         await self.db_session.commit()
    #         await self.db_session.refresh(new_lesson)
    #         return new_lesson
    #     except Exception as e:
    #         await self.db_session.rollback()
    #         raise e