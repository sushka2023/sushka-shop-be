from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import Optional

from src.conf.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

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
            message_body = (
                f"Dear Madam,\n\nMy name is {name}\nMy email: {email}\n"
                f"My phone number: {phone_number}\nMessage: {message}\n\n\n\n\n"
                f"Best regards,\n\n{name}"
            )
            message_schema = MessageSchema(
                subject=f"New Message from {name}",
                recipients=[email_owner],
                body=message_body,
                subtype="plain",
            )
            await self.mail.send_message(message=message_schema)
        except Exception as e:
            raise e


email_service = EmailService()
