from sqlalchemy import INTEGER, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class PLanguageModel(Base):
    __tablename__ = 'programming_languages'
    language_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True, comment='Unique identifier for the programming language')
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, comment='Name of the programming language', index=True)

    # relationships
    users: Mapped[list['UserModel']] = relationship(back_populates='active_language')
    lessons: Mapped[list['LessonModel']] = relationship(back_populates='programming_language', cascade="all, delete-orphan")
