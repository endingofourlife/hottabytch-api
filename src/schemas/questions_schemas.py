from pydantic import BaseModel


class QuestionAnswer(BaseModel):
    answer_id: int
    text: str


class QuestionResponse(BaseModel):
    question_id: int
    text: str
    answers: list[QuestionAnswer] = []
    lesson_id: int

class QuestionCreateResponse(BaseModel):
    question_id: int
    text: str
    answers: list[QuestionAnswer] = []
    lesson_id: int

class QuestionAnswerCreate(BaseModel):
    text: str
    is_correct: bool

class QuestionCreate(BaseModel):
    text: str
    answers: list[QuestionAnswerCreate]
    lesson_id: int

