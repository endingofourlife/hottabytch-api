from fastapi import APIRouter

from .lessons_router import lessons_router
from .user_router import user_router
from .p_language_router import p_language_router
from .question_router import question_router

v1_router = APIRouter()

v1_router.include_router(user_router, prefix='/user', tags=['users'])
v1_router.include_router(p_language_router, prefix='/language', tags=['programming languages'])
v1_router.include_router(lessons_router, prefix='/lessons', tags=['lessons'])
v1_router.include_router(question_router, prefix='/questions', tags=['questions'])