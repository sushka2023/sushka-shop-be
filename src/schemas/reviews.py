from datetime import datetime
from typing import Type

from pydantic import BaseModel, Field

from src.database.models import Rating, Image
from src.schemas.images import ImageResponseReview
from src.services.cloud_image import CloudImage


class ReviewModel(BaseModel):
    product_id: int
    rating: Rating
    description: str = Field(min_length=10, max_length=255)


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: Rating
    description: str
    created_at: datetime
    is_deleted: bool
    is_checked: bool
    images: list[ImageResponseReview]

    class Config:
        orm_mode = True


class ReviewArchiveModel(BaseModel):
    id: int


class ReviewCheckModel(BaseModel):
    id: int
