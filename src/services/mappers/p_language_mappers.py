from sqlalchemy import Sequence

from src.database.models import PLanguageModel
from src.schemas import LanguageResponse


class PLanguageMapper:
    @staticmethod
    def to_single(model: PLanguageModel) -> LanguageResponse:
        return LanguageResponse(
            id=model.language_id,
            name=model.name
        )

    @staticmethod
    def to_list(models: list[PLanguageModel] | Sequence[PLanguageModel]) -> list[LanguageResponse]:
        return [PLanguageMapper.to_single(model) for model in models]
