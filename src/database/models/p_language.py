from sqlalchemy import INTEGER, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class PLanguageModel(Base):
    __tablename__ = 'programming_languages'
    language_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    # Name of the programming language. e.g., Python, JavaScript, etc.
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    # A short description of the programming language. e.g. 'JS is the best for web development'
    description: Mapped[str] = mapped_column(String(200), nullable=False, server_default='')
    # URL of the programming language picture
    picture: Mapped[str] = mapped_column(String(100), nullable=False, server_default='')
    # Level of the programming language, e.g., 0 for beginner, 1 for intermediate, 2 for professional.
    level: Mapped[int] = mapped_column(INTEGER, nullable=False, default=0, server_default='0')
    # Popularity of the programming language. From 0 to 10. e.g. 3/10, 9/10, etc.
    popularity: Mapped[int] = mapped_column(INTEGER, nullable=False, default=0, server_default='0')

    # relationships
    # One user can have only one active programming language
    users: Mapped[list['UserModel']] = relationship(back_populates='active_language')
    # One programming language has many lessons
    lessons: Mapped[list['LessonModel']] = relationship(back_populates='programming_language', cascade="all, delete-orphan")
