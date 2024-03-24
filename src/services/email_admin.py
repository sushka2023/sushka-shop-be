import logging
from typing import Optional

from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from src.services.email import conf

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.mail = FastMail(conf)

    async def send_admin_email(self, email: EmailStr, order_id: int, message: Optional[str]):
        try:
            template_data = {
                "email": email,
                "order_id": order_id,
                "message": message
            }

            message_schema = MessageSchema(
                subject="Notification about the created order",
                recipients=[email],
                template_body=template_data,
                subtype=MessageType.html
            )
            await self.mail.send_message(message_schema, template_name="email_admin.html")
            logger.info("Email sent successfully from the Sushka Shop")
        except Exception as e:
            logger.error(f"Error sending email from the Sushka Shop: {str(e)}")
            raise e


email_admin_service = EmailService()
