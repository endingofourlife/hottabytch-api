from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import QuestionModel
from src.database.models.answer import AnswerModel
from src.schemas import QuestionAnswerCreate


class QuestionRepository:
    def __init__(self, session: AsyncSession):
        self.db_session = session

    async def create_question(self, text: str, answers: list[QuestionAnswerCreate], lesson_id: int) -> QuestionModel | None:
        try:
            new_question = QuestionModel(
                question_text=text,
                lesson_id=lesson_id,
                answers=[
                    AnswerModel(
                        answer_text=answer.text,
                        is_correct=answer.is_correct
                    ) for answer in answers
                ]
            )
            self.db_session.add(new_question)
            await self.db_session.commit()
            await self.db_session.refresh(new_question)
            return new_question
        except Exception as e:
            await self.db_session.rollback()
            raise e
