from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db
from src.core import handle_service_result
from src.repository import PLanguageRepository
from src.schemas import CreateLanguageRequest, LanguageResponse
from src.services import PLanguageService

p_language_router = APIRouter()

async def get_language_service(session: AsyncSession = Depends(get_db)) -> PLanguageService:
    return PLanguageService(PLanguageRepository(session))


@p_language_router.post('/add-language', summary='Add a new programming language', response_model=LanguageResponse)
async def add_language(request: CreateLanguageRequest, service: PLanguageService = Depends(get_language_service)):
    response = await service.add_language(request.name)
    return handle_service_result(response)

@p_language_router.get('/available-languages', summary='Get all available programming languages', response_model=list[LanguageResponse])
async def get_all_languages(service: PLanguageService = Depends(get_language_service)):
    response = await service.get_all_languages()
    return handle_service_result(response)
