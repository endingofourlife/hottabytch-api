from typing import Sequence

from src.database.models import LessonModel
from src.schemas.tests_schemas import StartLessonResponse, AnswerResponse, QuestionResponse, CreateLessonResponse, \
    SimplifiedLessonResponse, CheckLessonAnswerResponse, LessonResultResponse


class LessonsMapper:
    @staticmethod
    def to_start_lesson_response_cache(session_id: str, questions: list[dict]) -> StartLessonResponse:
        return StartLessonResponse(
            session_id=session_id,
            questions=[
                QuestionResponse(
                    question_id=question.get('question_id'),
                    text=question.get('question_text'),
                    answers=[
                        AnswerResponse(
                            answer_id=answer.get("answer_id"),
                            question_text=answer.get("answer_text")
                        )
                        for answer in question.get("answers")
                    ]
                )
                for question in questions
            ]
        )

    @staticmethod
    def to_start_lesson_response(session_id: str, lesson: LessonModel) -> StartLessonResponse:
        return StartLessonResponse(
            session_id=session_id,
            questions=[
                QuestionResponse(
                    question_id=question.question_id,
                    text=question.question_text,
                    answers=[
                        AnswerResponse(
                            answer_id=answer.answer_id,
                            question_text=answer.answer_text
                        )
                        for answer in question.answers
                    ]
                )
                for question in lesson.questions
            ]
        )

    @staticmethod
    def to_create_lesson_response(lesson: LessonModel) -> CreateLessonResponse:
        return CreateLessonResponse(
            test_id=lesson.lesson_id,
            language_id=lesson.language_id,
            title=lesson.title,
            description=lesson.description,
            questions=[]
        )

    @staticmethod
    def to_all_lessons_response(lessons: Sequence[LessonModel]) -> list[SimplifiedLessonResponse]:
        return [
            SimplifiedLessonResponse(
                test_id=lesson.lesson_id,
                language_id=lesson.language_id,
                title=lesson.title,
                description=lesson.description
            )
            for lesson in lessons
        ]

    @staticmethod
    def to_lesson_cache(lesson: LessonModel, correct_answers: dict[int, int]) -> dict:
        return {
            "lesson_id": lesson.lesson_id,
            "questions": [
                {
                    "question_id": question.question_id,
                    "question_text": question.question_text,
                    "answers": [
                        {
                            "answer_id": answer.answer_id,
                            "answer_text": answer.answer_text
                        }
                        for answer in question.answers
                    ]
                }
                for question in lesson.questions
            ],
            "correct_answers": correct_answers
        }

    @staticmethod
    def to_answer_check_response(question_id: str, is_correct: bool) -> CheckLessonAnswerResponse:
        return CheckLessonAnswerResponse(
            question_id=question_id,
            is_correct=is_correct
        )

    @staticmethod
    def to_lesson_result_response(xp_earned: int, success_percent: int) -> LessonResultResponse:
        return LessonResultResponse(
            xp_earned=xp_earned,
            success_percent=success_percent,
        )