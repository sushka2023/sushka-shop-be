from datetime import datetime

from pydantic import BaseModel

from src.database.models import PaymentsTypes, OrdersStatus
from src.schemas.product import ProductResponseForOrder


class OrderedProductResponse(BaseModel):
    id: int
    product_id: int
    products: ProductResponseForOrder
    price_id: int
    order_id: int
    quantity: int

    class Config:
        orm_mode = True


class OrderModel(BaseModel):
    payment_type: PaymentsTypes
    call_manager: bool


class OrderResponse(BaseModel):
    id: int
    user_id: int
    basket_id: int
    price_order: float
    payment_type: PaymentsTypes
    created_at: datetime
    confirmation_manager: bool
    confirmation_pay: bool
    call_manager: bool
    status_order: OrdersStatus
    ordered_products: list[OrderedProductResponse] = []

    class Config:
        orm_mode = True


class OrderConfirmModel(BaseModel):
    id: int
