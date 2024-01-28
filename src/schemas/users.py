from datetime import datetime
from typing import Optional
import re


from pydantic import BaseModel, Field, validator

from src.database.models import Role
from src.schemas.nova_poshta import NovaPoshtaDataResponse
from src.schemas.ukr_poshta import UkrPoshtaResponse

password_pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$")
email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]{5,}@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
phone_pattern = re.compile(r'^(?:\+380|380|0)\d{9}$')


class UserModel(BaseModel):
    email: str = Field(min_length=6, max_length=150)
    first_name: str = Field(min_length=3, max_length=150)
    last_name: str = Field(min_length=3, max_length=150)
    password_checksum: str = Field(min_length=8, max_length=255)

    @validator("password_checksum", pre=True)
    def validate_password(cls, password_checksum):
        if not password_pattern.match(password_checksum):
            raise ValueError(
                "Password is not valid! The password must consist of at least one lowercase, "
                "uppercase letter, number and symbols."
            )
        return password_checksum

    @validator("email", pre=True)
    def validate_email(cls, email):
        if not email_pattern.match(email):
            raise ValueError(
                "Email is not valid! The email can consist of 5simbols@, Latin letters, numbers, dots and _"
            )
        return email


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    created_at: datetime
    updated_at: Optional[datetime]
    refresh_token: Optional[str]
    is_deleted: bool
    is_blocked: bool
    is_active: bool

    class Config:
        orm_mode = True


class UserChangeRole(BaseModel):
    id: int
    role: Role
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class UserUpdateData(BaseModel):
    first_name: str = Field(min_length=3, max_length=150)
    last_name: str = Field(min_length=3, max_length=150)
    phone_number: str = Field(min_length=10, max_length=13)

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, phone_number):
        if not phone_pattern.match(phone_number):
            raise ValueError(
                'Phone number is not valid! The phone number must first consist of the symbols "+380" '
                'or "380" or "0" and than followed by nine digits.'
            )
        return phone_number


class UserResponseAfterUpdate(UserUpdateData):
    email: str
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


class UserResponseForCRM(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    is_blocked: bool
    is_active: bool

    class Config:
        orm_mode = True


class PostResponseOrder(BaseModel):
    id: int
    user_id: int
    ukr_poshta: Optional[list[UkrPoshtaResponse]] = []
    nova_poshta: Optional[list[NovaPoshtaDataResponse]] = []

    class Config:
        orm_mode = True


class UserResponseForOrder(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    phone_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    is_blocked: bool
    is_active: bool
    posts: PostResponseOrder

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordModel(BaseModel):
    password_checksum: str = Field(min_length=8, max_length=255)

    @validator("password_checksum", pre=True)
    def validate_password(cls, password_checksum):
        if not password_pattern.match(password_checksum):
            raise ValueError(
                "Password is not valid! The password must consist of at least one lowercase, "
                "uppercase letter, number and symbols."
            )
        return password_checksum


class UserBlockOrRemoveModel(BaseModel):
    id: int
