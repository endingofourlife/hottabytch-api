from datetime import datetime
from typing import Optional

from sqlalchemy import INTEGER, String, BIGINT, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class UserModel(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, comment='Telegram user ID')
    first_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="First name of the user")
    # username: Mapped[str] = mapped_column(String(50), nullable=True, unique=True, comment="Unique username of the user. Got from the telegram profile")
    streak: Mapped[int] = mapped_column(INTEGER, nullable=False, default=0, comment="Current streak of consecutive days")
    last_lesson_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True, comment="Date of the last completed lesson", index=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", comment="Timezone of the user, default is UTC", server_default='UTC')
    xp: Mapped[int] = mapped_column(INTEGER, nullable=False, default=0, comment="Total XP earned by the user")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, default=func.now(), comment="Date when the user was created")

    # relationships
    active_language_id: Mapped[Optional[int]] = mapped_column(ForeignKey('programming_languages.language_id'), comment="ID of the active programming language")
    active_language: Mapped['PLanguageModel'] = relationship(back_populates='users')

    progress_records: Mapped[list['UserProgressModel']] = relationship(back_populates='user', cascade="all, delete-orphan")
