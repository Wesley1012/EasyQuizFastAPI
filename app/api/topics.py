from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.models.topic import Topic
from app.models.question import Question
from app.schemas.topic import TopicResponse, TopicCreate, TopicUpdate

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/", response_model=List[TopicResponse])
async def get_topics(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    """Получить список всех тем"""
    # Загружаем темы с вопросами
    query = (
        select(Topic)
        .where(Topic.is_active == True)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Topic.questions))  # ← Загружаем вопросы
    )
    result = await db.execute(query)
    topics = result.scalars().all()

    # Подсчитываем количество вопросов для каждой темы
    for topic in topics:
        topic.questions_count = len(topic.questions)  # ← Теперь работает

    return topics


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
        topic_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получить тему по ID"""
    query = (
        select(Topic)
        .where(Topic.id == topic_id)
        .options(selectinload(Topic.questions))  # ← Загружаем вопросы
    )
    result = await db.execute(query)
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    topic.questions_count = len(topic.questions)
    return topic


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
        topic: TopicCreate,
        db: AsyncSession = Depends(get_db)
):
    """Создать новую тему (админка)"""
    db_topic = Topic(**topic.model_dump())
    db.add(db_topic)
    await db.commit()
    await db.refresh(db_topic)
    return db_topic


@router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(
        topic_id: int,
        topic_update: TopicUpdate,
        db: AsyncSession = Depends(get_db)
):
    """Обновить тему (админка)"""
    query = select(Topic).where(Topic.id == topic_id)
    result = await db.execute(query)
    db_topic = result.scalar_one_or_none()

    if not db_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    for key, value in topic_update.model_dump(exclude_unset=True).items():
        setattr(db_topic, key, value)

    await db.commit()
    await db.refresh(db_topic)
    return db_topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
        topic_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Удалить тему (админка)"""
    query = select(Topic).where(Topic.id == topic_id)
    result = await db.execute(query)
    db_topic = result.scalar_one_or_none()

    if not db_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    await db.delete(db_topic)
    await db.commit()
    return {"message": "Topic deleted successfully"}