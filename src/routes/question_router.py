from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db
from src.core import handle_service_result
from src.repository import QuestionRepository
from src.schemas import QuestionCreate, QuestionCreateResponse
from src.services import QuestionService

question_router = APIRouter()

async def get_question_service(session: AsyncSession = Depends(get_db)) -> QuestionService:
    return QuestionService(QuestionRepository(session))

@question_router.post('/', response_model=QuestionCreateResponse)
async def create_question(question: QuestionCreate, service: QuestionService = Depends(get_question_service)):
    result = await service.create_question(question)
    return handle_service_result(result)