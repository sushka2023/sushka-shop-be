from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, Field, validator

from src.database.models import Role


password_pattern = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$')
email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]{5,}@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


class UserModel(BaseModel):
    email: str = Field(min_length=6, max_length=150)
    first_name: str = Field(min_length=3, max_length=150)
    last_name: str = Field(min_length=3, max_length=150)
    password_checksum: str = Field(min_length=8, max_length=255)

    @validator('password_checksum', pre=True)
    def validate_password(cls, password_checksum):
        if not password_pattern.match(password_checksum):
            raise ValueError('Password is not valid! The password must consist of at least one lowercase, uppercase letter, number and symbols.')
        return password_checksum

    @validator('email', pre=True)
    def validate_email(cls, email):
        if not email_pattern.match(email):
            raise ValueError('Email is not valid! The email can consist of 5simbols@, Latin letters, numbers, dots and _')
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

    class Config:
        orm_mode = True


class UserChangeRole(BaseModel):
    id: int
    role: Role
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PasswordModel(BaseModel):
    password_checksum: str = Field(min_length=8, max_length=255)
