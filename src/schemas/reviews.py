from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import Rate


class ReviewModel(BaseModel):
    product_id: int
    rate: Rate
    description: str = Field(min_length=10, max_length=255)
    image_id: Optional[int] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rate: Rate
    description: str
    image_id: Optional[int] = None
    created_at: datetime
    is_deleted: bool
    is_checked: bool

    class Config:
        orm_mode = True
