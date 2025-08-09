from sqlalchemy import INTEGER, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class QuestionModel(Base):
    __tablename__ = 'questions'

    question_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True, comment='Unique identifier for the question')
    question_text: Mapped[str] = mapped_column(String(500), nullable=False, comment='Question text')

    # relationships
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.lesson_id'), comment="ID of the lesson this question belongs to")
    lesson: Mapped['LessonModel'] = relationship(back_populates='questions')

    answers: Mapped[list['AnswerModel']] = relationship('AnswerModel',
                                                        back_populates='question',
                                                        cascade='all, delete-orphan')
