import logging

from fastapi_mail import FastMail, MessageSchema, MessageType

from src.services.email import conf

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.mail = FastMail(conf)

    async def send_order_confirmation_email(self, order_data: dict):
        try:
            template_data = {
                "order_id": order_data["order_id"],
                "total_price": order_data["total_price"],
                "customer": order_data["customer"],
                "email_customer": order_data["email_customer"],
                "phone_number_customer": order_data["phone_number_customer"],
                "full_name_another_recipient": order_data["full_name_another_recipient"],
                "phone_number_another_recipient": order_data["phone_number_another_recipient"],
                "delivery_mode": order_data["delivery_mode"],
                "address_delivery": order_data["address_delivery"],
                "payment_mode": order_data["payment_mode"],
                "ordered_products": order_data["ordered_products"],
            }

            message_schema = MessageSchema(
                subject="Order confirmation",
                recipients=[order_data["email_customer"]],
                template_body=template_data,
                subtype=MessageType.html
            )
            await self.mail.send_message(message_schema, template_name="order_to_email.html")
            logger.info("Email sent successfully from the Sushka Shop")
        except Exception as e:
            logger.error(f"Error sending email from the Sushka Shop: {str(e)}")
            raise e


email_service = EmailService()
