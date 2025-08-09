from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db, get_redis_client
from src.core import handle_service_result
from src.repository import LessonsRepository
from src.schemas.tests_schemas import StartLessonRequest, StartLessonResponse, CheckLessonAnswerResponse, \
    CheckLessonAnswerRequest, LessonResultResponse, LessonCreateRequest, CreateLessonResponse, SimplifiedLessonResponse, \
    ActualLessonResponse
from src.services import LessonsService

lessons_router = APIRouter()

async def get_lesson_service(session: AsyncSession = Depends(get_db), redis_client: Redis = Depends(get_redis_client)) -> LessonsService:
    return LessonsService(LessonsRepository(session), redis_client)

@lessons_router.post('/start', response_model=StartLessonResponse)
async def start_lesson(request: StartLessonRequest, service: LessonsService = Depends(get_lesson_service)):
    result = await service.start_lesson(request)
    return handle_service_result(result)

@lessons_router.post('/check', response_model=CheckLessonAnswerResponse)
async def check_lesson_answer(request: CheckLessonAnswerRequest, service: LessonsService = Depends(get_lesson_service)):
    result = await service.check_lesson_answer(request)
    return handle_service_result(result)

@lessons_router.get('/result/{session_id}', response_model=LessonResultResponse)
async def get_lesson_result(session_id: str, service: LessonsService = Depends(get_lesson_service)):
    result = await service.get_lesson_result(session_id)
    return handle_service_result(result)

@lessons_router.post('/add-lesson', response_model=CreateLessonResponse)
async def create_lesson(request: LessonCreateRequest, service: LessonsService = Depends(get_lesson_service)):
    result = await service.create_lesson(request)
    return handle_service_result(result)

@lessons_router.get('/all', response_model=list[SimplifiedLessonResponse])
async def get_all_lessons(service: LessonsService = Depends(get_lesson_service)):
    result = await service.get_all_lessons()
    return handle_service_result(result)

@lessons_router.get('/actual-lesson/{user_id}', response_model=ActualLessonResponse)
async def get_actual_lesson(user_id: int, service: LessonsService = Depends(get_lesson_service)):
    result = await service.get_actual_lesson(user_id)
    return handle_service_result(result)