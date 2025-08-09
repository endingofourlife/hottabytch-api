from datetime import datetime

from sqlalchemy import INTEGER, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base

class UserProgressModel(Base):
    __tablename__ = 'user_progress'

    progress_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True, comment='Unique identifier for the user progress record')
    completed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=func.now(), comment='Timestamp when the lesson was completed')
    xp_earned: Mapped[int] = mapped_column(INTEGER, nullable=False, default=0, comment='XP earned for completing the lesson')
    success_percent: Mapped[int] = mapped_column(INTEGER, nullable=False, default=0, comment='Success percentage for the completed lesson')

    # relationships
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), comment='ID of the user who completed the lesson')
    user: Mapped['UserModel'] = relationship(back_populates='progress_records')

    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.lesson_id'), comment='ID of the lesson that was completed')
    lesson: Mapped['LessonModel'] = relationship()
