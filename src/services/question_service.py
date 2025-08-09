from src.repository import QuestionRepository
from src.schemas import QuestionCreate, QuestionCreateResponse
from src.services import ServiceResult
from src.services.mappers import QuestionsMapper


class QuestionService:
    def __init__(self, repository: QuestionRepository):
        self._repository = repository

    async def create_question(self, request: QuestionCreate) -> ServiceResult[QuestionCreateResponse]:
        try:
            if len(request.answers) != 4:
                return ServiceResult.failure('Exactly 4 answers required', status_code=400)
            if sum(1 for answer in request.answers if answer.is_correct) != 1:
                return ServiceResult.failure('Exactly one correct answer required', status_code=400)

            new_question = await self._repository.create_question(
                text=request.text,
                answers=request.answers,
                lesson_id=request.lesson_id
            )
            if not new_question:
                return ServiceResult.failure('Failed to create question', status_code=400)
            return ServiceResult.success(QuestionsMapper.to_create_question_response(new_question))
        except Exception as e:
            return ServiceResult.failure(f'Error creating question: {str(e)}', status_code=500)
