from pydantic import BaseModel
from typing import Optional, List


class AnswerBase(BaseModel):
    text: str
    is_correct: bool = False


class AnswerCreate(AnswerBase):
    pass


class AnswerResponse(AnswerBase):
    id: int

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    text: str
    image_url: Optional[str] = None
    order: int = 0


class QuestionCreate(QuestionBase):
    topic_id: int  # ← Добавляем это поле!
    answers: List[AnswerCreate]


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    image_url: Optional[str] = None
    order: Optional[int] = None
    topic_id: Optional[int] = None  # ← Добавляем для обновления


class QuestionResponse(QuestionBase):
    id: int
    topic_id: int
    answers: List[AnswerResponse] = []

    class Config:
        from_attributes = True


# Для пользователя (без правильных ответов)
class QuestionForUser(QuestionBase):
    id: int
    answers: List[AnswerResponse]  # is_correct будет скрыт на фронте

    class Config:
        from_attributes = True