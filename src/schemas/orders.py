from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.database.models import PaymentsTypes, OrdersStatus, PostType
from src.schemas.price import PriceResponse
from src.schemas.product import ProductResponseForOrder
from src.schemas.users import UserResponseForOrder


class OrderedProductResponse(BaseModel):
    id: int
    product_id: int
    products: ProductResponseForOrder
    price_id: int
    prices: PriceResponse
    order_id: int
    quantity: int

    class Config:
        orm_mode = True


class OrderModel(BaseModel):
    payment_type: PaymentsTypes
    call_manager: bool
    is_another_recipient: bool
    full_name_another_recipient: Optional[str] = ""
    phone_number_another_recipient: Optional[str] = ""


class OrderResponse(BaseModel):
    id: int
    user_id: int
    user: UserResponseForOrder
    is_another_recipient: bool
    full_name_another_recipient: Optional[str] = ""
    phone_number_another_recipient: Optional[str] = ""
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


class OrderMessageResponse(BaseModel):
    message: str


class OrderCreateResponse(BaseModel):
    id: int
    is_authenticated: bool

    class Config:
        orm_mode = True


class OrderItemsModel(BaseModel):
    product_id: int
    price_id: Optional[int]
    quantity: int = 1


class OrderedItemsResponse(BaseModel):
    order_id: int
    product_id: int
    product: ProductResponseForOrder
    price_id: int
    prices: PriceResponse
    quantity: int

    class Config:
        orm_mode = True


class OrderAnonymUserModel(BaseModel):
    first_name_anon_user: str
    last_name_anon_user: str
    email_anon_user: EmailStr
    phone_number_anon_user: Optional[str] = ""
    is_another_recipient: bool
    full_name_another_recipient: Optional[str] = ""
    phone_number_another_recipient: Optional[str] = ""
    post_type: PostType
    country: Optional[str] = ""
    city: str
    address_warehouse: Optional[str] = ""
    area: Optional[str] = ""
    region: Optional[str] = ""
    street: Optional[str] = ""
    house_number: Optional[str] = ""
    apartment_number: Optional[str] = ""
    floor: Optional[int] = None
    post_code: Optional[str] = ""
    payment_type: PaymentsTypes
    call_manager: bool


class OrderAnonymUserResponse(BaseModel):
    id: int
    price_order: float
    first_name_anon_user: str
    last_name_anon_user: str
    email_anon_user: EmailStr
    phone_number_anon_user: Optional[str] = ""
    is_another_recipient: bool
    full_name_another_recipient: Optional[str] = ""
    phone_number_another_recipient: Optional[str] = ""
    post_type: PostType
    country: Optional[str] = ""
    city: str
    address_warehouse: Optional[str] = ""
    area: Optional[str] = ""
    region: Optional[str] = ""
    street: Optional[str] = ""
    house_number: Optional[str] = ""
    apartment_number: Optional[str] = ""
    floor: Optional[int] = None
    post_code: Optional[str] = ""
    payment_type: PaymentsTypes
    created_at: datetime
    confirmation_manager: bool
    confirmation_pay: bool
    call_manager: bool
    is_authenticated: bool
    is_created: bool
    status_order: OrdersStatus
    ordered_products: list[OrderedProductResponse] = []

    class Config:
        orm_mode = True


class UpdateOrderStatus(BaseModel):
    new_status: OrdersStatus


class OrdersCRMResponse(BaseModel):
    id: int
    price_order: float
    user_id: Optional[int] = None
    user: Optional[UserResponseForOrder] = {}
    basket_id: Optional[int] = None
    first_name_anon_user: Optional[str] = ""
    last_name_anon_user: Optional[str] = ""
    email_anon_user: Optional[EmailStr] = ""
    phone_number_anon_user: Optional[str] = ""
    is_another_recipient: bool
    full_name_another_recipient: Optional[str] = ""
    phone_number_another_recipient: Optional[str] = ""
    comment: Optional[str] = ""
    post_type: PostType
    country: Optional[str] = ""
    city: Optional[str] = ""
    address_warehouse: Optional[str] = ""
    area: Optional[str] = ""
    region: Optional[str] = ""
    street: Optional[str] = ""
    house_number: Optional[str] = ""
    apartment_number: Optional[str] = ""
    floor: Optional[int] = None
    post_code: Optional[str] = ""
    payment_type: PaymentsTypes
    created_at: datetime
    confirmation_manager: bool
    confirmation_pay: bool
    call_manager: bool
    is_authenticated: bool
    is_created: bool
    status_order: OrdersStatus
    ordered_products: list[OrderedProductResponse] = []

    class Config:
        orm_mode = True
