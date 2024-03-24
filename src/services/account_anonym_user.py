import logging

from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.services.email import conf

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.mail = FastMail(conf)

    async def send_account_email(self, email: EmailStr, password: str):
        try:
            template_data = {
                "email": email,
                "password": password,
            }

            message_schema = MessageSchema(
                subject="Account confirmation",
                recipients=[email],
                template_body=template_data,
                subtype=MessageType.html
            )
            await self.mail.send_message(message_schema, template_name="account_anonym_user.html")
            logger.info("Email sent successfully from the Sushka Shop")
        except Exception as e:
            logger.error(f"Error sending email from the Sushka Shop: {str(e)}")
            raise e


email_account_service = EmailService()
