from typing import Optional

from pydantic import BaseModel

from src.schemas.product import ProductResponse


class AnonymousUserResponse(BaseModel):
    id: int
    user_anon_id: str

    class Config:
        orm_mode = True


class BasketAnonUserResponse(BaseModel):
    id: int
    anonymous_user_id: int
    anonymous_user: AnonymousUserResponse

    class Config:
        orm_mode = True


class BasketItemAnonUserModel(BaseModel):
    product_id: int
    price_id_by_anon_user: Optional[int]
    quantity: int = 1


class BasketItemAnonUserResponse(BaseModel):
    id: int
    basket_anon_user_id: int
    product_id: int
    product: ProductResponse
    price_id_by_anon_user: int
    quantity: int

    class Config:
        orm_mode = True


class BasketItemAnonUserRemoveModel(BaseModel):
    product_id: int


class ChangeQuantityBasketItemModel(BaseModel):
    id: int
    quantity: int


class BasketItemAnonUserMessage(BaseModel):
    message: str
