import re
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

phone_pattern = re.compile(r'^(?:\+380|380|0)\d{9}$')


class CooperationModel(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = ""
    message: Optional[str] = ""

    @validator("phone_number", pre=True)
    def validate_phone_number(cls, phone_number):
        if phone_number:
            if not phone_pattern.match(phone_number):
                raise ValueError(
                    'Phone number is not valid! The phone number must first consist of the symbols "+380" '
                    'or "380" or "0" and than followed by nine digits.'
                )
            return phone_number
        return ""
