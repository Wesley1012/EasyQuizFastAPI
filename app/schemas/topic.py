from pydantic import BaseModel
from typing import Optional


class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class TopicCreate(TopicBase):
    pass


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TopicResponse(TopicBase):
    id: int
    questions_count: Optional[int] = 0

    class Config:
        from_attributes = True