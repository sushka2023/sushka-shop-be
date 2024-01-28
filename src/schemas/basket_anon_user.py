from typing import Optional

from pydantic import BaseModel

from src.schemas.product import ProductResponse


class BasketAnonUserModel(BaseModel):
    product_id: int
    price_id_by_anon_user: Optional[int]
    quantity: int = 1


class BasketAnonUserResponse(BaseModel):
    id: int
    product_id: int
    product: ProductResponse
    price_id_by_anon_user: int
    quantity: int

    class Config:
        orm_mode = True


class BasketAnonUserRemoveModel(BaseModel):
    product_id: int


class ChangeQuantityBasketItemModel(BaseModel):
    id: int
    quantity: int
