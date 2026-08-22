from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel  # ← Добавляем

from app.core.database import get_db
from app.models.user_answer import UserAnswer
from app.models.question import Question
from app.models.answer import Answer
from app.models.topic import Topic
from app.schemas.statistics import UserStatistics, TopicStatistics

router = APIRouter(prefix="/statistics", tags=["statistics"])


# Создаем Pydantic модель для запроса
class SubmitAnswerRequest(BaseModel):
    question_id: int
    selected_answer_id: int
    user_id: Optional[str] = None


@router.post("/submit-answer")
async def submit_answer(
        request: SubmitAnswerRequest,  # ← Используем Pydantic модель
        db: AsyncSession = Depends(get_db)
):
    """Сохранение ответа пользователя"""
    # Генерируем user_id если его нет
    user_id = request.user_id or str(uuid4())

    # Проверяем, существует ли вопрос
    question_query = select(Question).where(Question.id == request.question_id)
    question_result = await db.execute(question_query)
    question = question_result.scalar_one_or_none()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Проверяем, существует ли ответ
    answer_query = select(Answer).where(Answer.id == request.selected_answer_id)
    answer_result = await db.execute(answer_query)
    answer = answer_result.scalar_one_or_none()

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )

    # Проверяем, принадлежит ли ответ этому вопросу
    if answer.question_id != request.question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer does not belong to this question"
        )

    # Проверяем, не отвечал ли пользователь уже на этот вопрос
    existing_query = select(UserAnswer).where(
        UserAnswer.user_id == user_id,
        UserAnswer.question_id == request.question_id
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already answered this question"
        )

    # Сохраняем ответ пользователя
    user_answer = UserAnswer(
        user_id=user_id,
        question_id=request.question_id,
        selected_answer_id=request.selected_answer_id,
        is_correct=answer.is_correct
    )
    db.add(user_answer)
    await db.commit()

    # Находим правильный ответ
    correct_answer_query = select(Answer).where(
        Answer.question_id == request.question_id,
        Answer.is_correct == True
    )
    correct_result = await db.execute(correct_answer_query)
    correct_answer = correct_result.scalar_one_or_none()

    return {
        "is_correct": answer.is_correct,
        "correct_answer_id": correct_answer.id if correct_answer else None,
        "user_id": user_id
    }


@router.get("/{user_id}", response_model=UserStatistics)
async def get_user_statistics(
        user_id: str,
        db: AsyncSession = Depends(get_db)
):
    """Получение статистики пользователя"""
    # Получаем все ответы пользователя с вопросами
    query = (
        select(UserAnswer)
        .where(UserAnswer.user_id == user_id)
    )
    result = await db.execute(query)
    user_answers = result.scalars().all()

    if not user_answers:
        return UserStatistics(
            total_answered=0,
            correct_count=0,
            wrong_count=0,
            success_rate=0.0,
            topics=[]
        )

    # Считаем общую статистику
    correct_count = sum(1 for ua in user_answers if ua.is_correct)
    wrong_count = len(user_answers) - correct_count
    success_rate = (correct_count / len(user_answers)) * 100 if user_answers else 0

    # Группируем по темам
    topics_stats = []
    topic_ids = set()

    for ua in user_answers:
        question = await db.get(Question, ua.question_id)
        if question:
            topic_ids.add(question.topic_id)

    for tid in topic_ids:
        topic = await db.get(Topic, tid)
        if topic:
            # Получаем ответы для этой темы
            topic_answers = []
            for ua in user_answers:
                question = await db.get(Question, ua.question_id)
                if question and question.topic_id == tid:
                    topic_answers.append(ua)

            topic_correct = sum(1 for ua in topic_answers if ua.is_correct)
            topics_stats.append(TopicStatistics(
                topic_id=topic.id,
                topic_name=topic.name,
                total_questions=len(topic_answers),
                correct_answers=topic_correct,
                wrong_answers=len(topic_answers) - topic_correct,
                percentage=(topic_correct / len(topic_answers)) * 100 if topic_answers else 0
            ))

    return UserStatistics(
        total_answered=len(user_answers),
        correct_count=correct_count,
        wrong_count=wrong_count,
        success_rate=success_rate,
        topics=topics_stats
    )