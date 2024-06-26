from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.database.models import PaymentsTypes, OrdersStatus, PostType
from src.schemas.nova_poshta import NovaPoshtaDataResponse
from src.schemas.price import PriceResponse
from src.schemas.product import ProductResponseForOrder
from src.schemas.ukr_poshta import UkrPoshtaResponse
from src.schemas.users import UserResponseForOrder


class OrderedProductModel(BaseModel):
    product_id: int
    price_id: Optional[int]
    quantity: int = 1


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
    phone_number_current_user: Optional[str] = ""
    selected_nova_poshta_id: Optional[int] = Field(default_factory=lambda: None)
    selected_ukr_poshta_id: Optional[int] = Field(default_factory=lambda: None)
    payment_type: PaymentsTypes
    call_manager: bool
    is_another_recipient: Optional[bool] = False
    full_name_another_recipient: Optional[str] = ""
    phone_number_another_recipient: Optional[str] = ""
    comment: Optional[str] = ""


class OrderResponse(BaseModel):
    id: int
    user_id: int
    user: UserResponseForOrder
    is_another_recipient: Optional[bool]
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
    post_type: PostType
    selected_nova_poshta_id: int = None
    selected_nova_poshta: Optional[NovaPoshtaDataResponse] = None
    selected_ukr_poshta_id: int = None
    selected_ukr_poshta: Optional[UkrPoshtaResponse] = None
    ordered_products: list[OrderedProductResponse] = []
    comment: Optional[str] = ""

    class Config:
        orm_mode = True


class OrderConfirmModel(BaseModel):
    id: int


class OrderMessageResponse(BaseModel):
    message: str


class OrderAnonymUserModel(BaseModel):
    first_name_anon_user: str
    last_name_anon_user: str
    email_anon_user: EmailStr
    phone_number_anon_user: str
    is_another_recipient: Optional[bool] = False
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
    ordered_products: list[OrderedProductModel]
    comment: Optional[str] = ""


class OrderAnonymUserResponse(BaseModel):
    id: int
    price_order: float
    user_id: Optional[int] = None
    user: Optional[UserResponseForOrder] = {}
    basket_id: Optional[int] = None
    first_name_anon_user: str
    last_name_anon_user: str
    email_anon_user: EmailStr
    phone_number_anon_user: Optional[str] = ""
    is_another_recipient: Optional[bool]
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
    status_order: OrdersStatus
    ordered_products: list[OrderedProductResponse] = []
    comment: Optional[str] = ""

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
    is_another_recipient: Optional[bool]
    full_name_another_recipient: Optional[str] = ""
    phone_number_another_recipient: Optional[str] = ""
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
    status_order: OrdersStatus
    selected_nova_poshta_id: int = None
    selected_nova_poshta: Optional[NovaPoshtaDataResponse] = None
    selected_ukr_poshta_id: int = None
    selected_ukr_poshta: Optional[UkrPoshtaResponse] = None
    ordered_products: list[OrderedProductResponse] = []
    comment: Optional[str] = ""
    notes_admin: Optional[str] = ""

    class Config:
        orm_mode = True


class OrderAdminNotesModel(BaseModel):
    notes: str


class OrdersCurrentUserWithTotalCountResponse(BaseModel):
    orders: list[OrderResponse]
    total_count: int


class OrdersCRMWithTotalCountResponse(BaseModel):
    orders: list[OrdersCRMResponse] = []
    total_count: int


class OrdersResponseWithMessage(BaseModel):
    message: str
    order_info: OrderAnonymUserResponse


class OrdersWithMessage(BaseModel):
    message: str
    order_info: OrderResponse
