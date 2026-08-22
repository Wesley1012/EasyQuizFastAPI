from hyperadmin import Admin
from hyperadmin.core.registry import site
from hyperadmin.adapters.sqlalchemy import SQLAlchemyAdapter
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.topic import Topic
from app.models.question import Question
from app.models.answer import Answer


def setup_admin(app, engine: AsyncEngine):
    """Настройка админ-панели"""
    admin = Admin(app, engine=engine)

    # Регистрируем модели с адаптером SQLAlchemy
    site.register(Topic, adapter_class=SQLAlchemyAdapter)
    site.register(Question, adapter_class=SQLAlchemyAdapter)
    site.register(Answer, adapter_class=SQLAlchemyAdapter)

    # Монтируем админку
    admin.mount("/admin")

    return admin