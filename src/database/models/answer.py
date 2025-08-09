from sqlalchemy import INTEGER, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class AnswerModel(Base):
    __tablename__ = 'answers'

    answer_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True, comment='Unique identifier for the answer')
    answer_text: Mapped[str] = mapped_column(String(255), nullable=False, comment='Text of the answer')
    is_correct: Mapped[bool] = mapped_column(INTEGER, nullable=False, comment='Indicates if the answer is correct (1 for true, 0 for false)')


    # relationships
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.question_id'), nullable=False, comment='ID of the question this answer belongs to')
    question: Mapped['QuestionModel'] = relationship(back_populates='answers')