from typing import Optional

from pydantic import BaseModel, EmailStr


class CooperationModel(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = ""
    message: Optional[str] = ""
