from src.database.models import QuestionModel
from src.schemas import QuestionCreateResponse, QuestionAnswer


class QuestionsMapper:
    @staticmethod
    def to_create_question_response(question: QuestionModel) -> QuestionCreateResponse:
        return QuestionCreateResponse(
            question_id=question.question_id,
            text=question.question_text,
            answers=[],
            lesson_id=question.lesson_id
        )
