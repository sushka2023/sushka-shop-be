from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from typing import Optional

from src.conf.config import settings
from src.services.email import conf

email_owner = settings.email_recipients


class EmailService:
    def __init__(self):
        self.mail = FastMail(conf)

    async def send_email(
        self,
        name: str,
        email: EmailStr,
        phone_number: Optional[str],
        message: Optional[str],
    ):
        try:
            template_data = {
                "name": name,
                "email": email,
                "phone_number": phone_number,
                "message": message,
            }
            message_schema = MessageSchema(
                subject=f"New Message from {name}",
                recipients=[email_owner],
                template_body=template_data,
                subtype=MessageType.html
            )
            await self.mail.send_message(message_schema, template_name="email_cooperation.html")
        except Exception as e:
            raise e


email_service = EmailService()
