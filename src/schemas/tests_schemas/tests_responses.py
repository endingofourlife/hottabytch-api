from pydantic import BaseModel

class AnswerResponse(BaseModel):
    answer_id: int
    answer_text: str

class QuestionResponse(BaseModel):
    text: str
    question_id: int
    answers: list[AnswerResponse]

class StartLessonResponse(BaseModel):
    session_id: str
    questions: list[QuestionResponse]

class CheckLessonAnswerResponse(BaseModel):
    question_id: int
    is_correct: bool

class LessonResultResponse(BaseModel):
    xp_earned: int
    success_percent: int

class CreateLessonResponse(BaseModel):
    test_id: int
    language_id: int
    title: str
    description: str
    questions: list = []

class SimplifiedLessonResponse(BaseModel):
    test_id: int
    language_id: int
    title: str
    description: str

class ActualLessonResponse(BaseModel):
    lesson_id: int
    title: str
    description: str