from sqlalchemy import String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)  # Сессия или JWT
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Внешние ключи
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    selected_answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"))

    # Связи
    question: Mapped["Question"] = relationship(back_populates="user_answers")
    selected_answer: Mapped["Answer"] = relationship()