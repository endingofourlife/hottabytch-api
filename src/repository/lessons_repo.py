from datetime import datetime, timedelta
from typing import Sequence
import pytz

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models import LessonModel, UserProgressModel, QuestionModel, UserModel


class LessonsRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def get_unfinished_lesson_with_tests(self, user_id: int, need_user: bool = False) -> LessonModel:
        if need_user:
            user = await self.db_session.get(UserModel, user_id)
            if not user:
                raise ValueError(f'User with id {user_id} not found')
            if user.last_lesson_date:
                user_timezone = pytz.timezone(str(user.timezone)) if user.timezone else pytz.UTC
                last_date = user.last_lesson_date.astimezone(user_timezone).date()
                today = datetime.now(user_timezone).date()

                if last_date == today:
                    raise ValueError('User has already completed a lesson today')

        query = (
            select(LessonModel)
            .where(
                ~LessonModel.lesson_id.in_(
                    select(UserProgressModel.lesson_id)
                    .where(UserProgressModel.user_id == user_id)
                )
            )
            .order_by(LessonModel.lesson_id)
            .limit(1)
        )

        result = await self.db_session.execute(query)
        return result.unique().scalars().first()

    async def get_all_lessons(self) -> Sequence[LessonModel]:
        query = select(LessonModel)
        result = await self.db_session.execute(query)
        return result.scalars().all()


    async def create_lesson(self, title: str, description: str, language_id: int) -> LessonModel:
        try:
            new_lesson = LessonModel(title=title,
                                     description=description,
                                     language_id=language_id)
            self.db_session.add(new_lesson)
            await self.db_session.commit()
            await self.db_session.refresh(new_lesson)
            return new_lesson
        except Exception as e:
            await self.db_session.rollback()
            raise e

    async def get_lesson_by_id(self, lesson_id: int) -> LessonModel:
        query = (
            select(LessonModel)
            .where(LessonModel.lesson_id == lesson_id)
            .options(
                joinedload(LessonModel.questions)
                .joinedload(QuestionModel.answers)
            )
        )
        result = await self.db_session.execute(query)
        return result.unique().scalars().first()

    async def save_user_progress(self, user_id: int, lesson_id: int, xp_earned: int, success_percent: int):
        try:
            progress = UserProgressModel(
                user_id=user_id,
                lesson_id=lesson_id,
                xp_earned=xp_earned,
                success_percent=success_percent
            )
            self.db_session.add(progress)

            user = await self.db_session.get(UserModel, user_id)
            if not user:
                raise ValueError(f'User with id {user_id} not found')
            user.xp += xp_earned

            # TODO check date and timezone. in the future remove it to the service layer
            timezone_str = user.timezone if user.timezone else 'UTC'
            try:
                user_timezone = pytz.timezone(timezone_str)
            except Exception as e:
                print('Invalid timezone:', timezone_str, e)
                user_timezone = pytz.UTC

            now = datetime.now(user_timezone)
            today = now.date()

            if user.last_lesson_date is None:
                user.streak = 1
            else:
                last_date = user.last_lesson_date.astimezone(user_timezone).date()
                if last_date == today:
                    raise ValueError('User has already completed a lesson today')
                elif last_date == today - timedelta(days=1):
                    user.streak += 1
                else:
                    user.streak = 1

            user.last_lesson_date = now

            await self.db_session.commit()
            await self.db_session.refresh(progress)
            return progress
        except Exception as e:
            await self.db_session.rollback()
            raise e