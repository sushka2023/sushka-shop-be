from pydantic import BaseModel

from src.schemas.product import ProductResponse


class FavoriteItemsModel(BaseModel):
    product_id: int


class FavoriteItemsResponse(BaseModel):
    id: int
    favorite_id: int
    product: ProductResponse

    class Config:
        orm_mode = True
