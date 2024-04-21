from sqlalchemy.orm import Session

from src.database.models import UsedEmailToken


async def get_email_token(email_token: str, db: Session) -> UsedEmailToken:
    return db.query(UsedEmailToken).filter_by(email_token=email_token).first()


async def add_email_token(email_token: str, db: Session) -> None:
    used_email_token = UsedEmailToken(email_token=email_token)

    db.add(used_email_token)
    db.commit()
