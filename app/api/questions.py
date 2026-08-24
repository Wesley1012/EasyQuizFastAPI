from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.auth import verify_admin
from app.core.database import get_db
from app.models.question import Question
from app.models.answer import Answer
from app.models.topic import Topic
from app.schemas.question import QuestionResponse, QuestionCreate, QuestionForUser, QuestionUpdate

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/topic/{topic_id}", response_model=List[QuestionForUser])
async def get_questions_by_topic(
        topic_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получить все вопросы для темы (без правильных ответов)"""
    # Проверяем, существует ли тема
    topic_query = select(Topic).where(Topic.id == topic_id)
    topic_result = await db.execute(topic_query)
    topic = topic_result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {topic_id} not found"
        )

    # Загружаем вопросы вместе с ответами
    query = (
        select(Question)
        .where(Question.topic_id == topic_id)
        .order_by(Question.order)
        .options(selectinload(Question.answers))  # ← Загружаем ответы
    )
    result = await db.execute(query)
    questions = result.scalars().all()

    # Скрываем правильные ответы для пользователя
    for question in questions:
        for answer in question.answers:
            answer.is_correct = False

    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
        question_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получить вопрос по ID"""
    query = (
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.answers))  # ← Загружаем ответы
    )
    result = await db.execute(query)
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found"
        )

    return question


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
        question: QuestionCreate,
        db: AsyncSession = Depends(get_db),
        admin: str = Depends(verify_admin)
):
    """Создать новый вопрос с ответами (админка)"""
    # Проверяем, существует ли тема
    topic_query = select(Topic).where(Topic.id == question.topic_id)
    topic_result = await db.execute(topic_query)
    topic = topic_result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with id {question.topic_id} not found. Please create a topic first."
        )

    # Проверяем, что есть хотя бы один правильный ответ
    correct_answers = [a for a in question.answers if a.is_correct]
    if not correct_answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one answer must be marked as correct"
        )

    # Создаем вопрос
    db_question = Question(
        text=question.text,
        image_url=question.image_url,
        order=question.order,
        topic_id=question.topic_id
    )
    db.add(db_question)
    await db.flush()

    # Создаем ответы
    for answer_data in question.answers:
        db_answer = Answer(
            text=answer_data.text,
            is_correct=answer_data.is_correct,
            question_id=db_question.id
        )
        db.add(db_answer)

    await db.commit()

    # Загружаем вопрос с ответами для возврата
    query = (
        select(Question)
        .where(Question.id == db_question.id)
        .options(selectinload(Question.answers))
    )
    result = await db.execute(query)
    created_question = result.scalar_one()

    return created_question


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
        question_id: int,
        question_update: QuestionUpdate,
        db: AsyncSession = Depends(get_db),
        admin: str = Depends(verify_admin),
):
    """Обновить вопрос (админка)"""
    query = (
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.answers))
    )
    result = await db.execute(query)
    db_question = result.scalar_one_or_none()

    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found"
        )

    # Если обновляем topic_id, проверяем существование темы
    if question_update.topic_id is not None:
        topic_query = select(Topic).where(Topic.id == question_update.topic_id)
        topic_result = await db.execute(topic_query)
        topic = topic_result.scalar_one_or_none()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with id {question_update.topic_id} not found"
            )

    # Обновляем поля
    update_data = question_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_question, key, value)

    await db.commit()
    await db.refresh(db_question)
    return db_question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int,
                          db: AsyncSession = Depends(get_db),
                          admin: str = Depends(verify_admin)):
    """Удалить вопрос (админка)"""
    query = select(Question).where(Question.id == question_id)
    result = await db.execute(query)
    db_question = result.scalar_one_or_none()

    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found"
        )

    await db.delete(db_question)
    await db.commit()
    return {"message": "Question deleted successfully"}