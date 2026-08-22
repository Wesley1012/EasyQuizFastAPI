from pydantic import BaseModel
from typing import List, Optional


class AnswerResult(BaseModel):
    question_id: int
    question_text: str
    selected_answer_id: int
    selected_answer_text: str
    is_correct: bool
    correct_answer_id: int
    correct_answer_text: str


class TopicStatistics(BaseModel):
    topic_id: int
    topic_name: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    percentage: float


class UserStatistics(BaseModel):
    total_answered: int
    correct_count: int
    wrong_count: int
    success_rate: float
    topics: List[TopicStatistics] = []