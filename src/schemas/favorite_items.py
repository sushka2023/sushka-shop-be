from pydantic import BaseModel


class FavoriteItemsModel(BaseModel):
    product_id: int


class FavoriteItemsResponse(BaseModel):
    id: int
    favorite_id: int
    product_id: int

    class Config:
        orm_mode = True
