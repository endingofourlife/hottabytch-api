from sqlalchemy import INTEGER, String, ForeignKey, BOOLEAN
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class LessonModel(Base):
    __tablename__ = 'lessons'

    lesson_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True, comment='Unique identifier for the lesson')
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment='Title of the lesson')
    description: Mapped[str] = mapped_column(String(500), nullable=True, comment='Description of the lesson', default="")

    # relationships
    language_id: Mapped[int] = mapped_column(ForeignKey('programming_languages.language_id'), comment="ID of the active programming language")
    programming_language: Mapped['PLanguageModel'] = relationship(back_populates='lessons')

    questions: Mapped[list['QuestionModel']] = relationship(back_populates='lesson', cascade="all, delete-orphan")
