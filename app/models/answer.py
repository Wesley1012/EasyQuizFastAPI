from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    # Внешний ключ к вопросу
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))

    # Связи
    question: Mapped["Question"] = relationship(back_populates="answers")