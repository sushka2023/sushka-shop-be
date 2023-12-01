from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import ImageType


class ImageModel(BaseModel):
    description: str = Field(min_length=1, max_length=255)
    image_type: ImageType
    product_id: int
    main_image: Optional[bool]


class ImageResponse(BaseModel):
    id: int
    product_id: Optional[int]
    image_url: str
    description: str = Field(min_length=1, max_length=255)
    image_type: ImageType
    main_image: bool

    class Config:
        orm_mode = True
