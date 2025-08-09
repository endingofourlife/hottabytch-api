from pydantic import BaseModel


class StartLessonRequest(BaseModel):
    user_id: int
    lesson_id: int

class CheckLessonAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer_id: int

class LessonCreateRequest(BaseModel):
    title: str
    description: str
    language_id: int
