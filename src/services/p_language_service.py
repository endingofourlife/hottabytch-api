from src.repository import PLanguageRepository
from src.schemas import LanguageResponse, CreateLanguageRequest
from src.services import ServiceResult
from src.services.mappers import PLanguageMapper


class PLanguageService:
    def __init__(self, repository: PLanguageRepository):
        self._repository = repository

    async def get_all_languages(self) -> ServiceResult[list[LanguageResponse]]:
        try:
            languages = await self._repository.get_all_languages()
            return ServiceResult.success(PLanguageMapper.to_list(languages))
        except Exception as e:
            return ServiceResult.failure(f'Error fetching languages: {str(e)}', status_code=500)

    async def add_language(self, request: CreateLanguageRequest) -> ServiceResult[LanguageResponse]:
        try:
            new_language = await self._repository.add_language(request.name, request.description, request.picture, request.level, request.popularity)
            return ServiceResult.success(PLanguageMapper.to_single(new_language))
        except Exception as e:
            return ServiceResult.failure(f'Error adding language: {str(e)}', status_code=400)

