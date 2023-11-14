from datetime import datetime

from pydantic import BaseModel

from src.database.models import PaymentType, OrderStatus


class OrderModel(BaseModel):
    payment_type: PaymentType
    call_manager: bool


class OrderResponse(BaseModel):
    id: int
    user_id: int
    basket_id: int
    price_order: float
    payment_type: PaymentType
    created_at: datetime
    confirmation_manager: bool
    confirmation_pay: bool
    call_manager: bool
    status_order: OrderStatus

    class Config:
        orm_mode = True


class OrderConfirmModel(BaseModel):
    id: int
