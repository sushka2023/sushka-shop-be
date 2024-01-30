from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import AnonymousUser, BasketNumberAnonUser
from src.services.exception_detail import ExDetail as Ex


async def create_anonymous_user(db: Session):
    user_anon_id = str(uuid4())  # Генеруємо унікальний ідентифікатор

    new_anon_user = AnonymousUser(user_anon_id=user_anon_id)

    db.add(new_anon_user)
    db.commit()
    db.refresh(new_anon_user)

    return new_anon_user


async def create_basket_for_anonymous_user(db: Session):
    anon_user = await create_anonymous_user(db=db)

    new_basket_number = BasketNumberAnonUser(anonymous_user_id=anon_user.id)

    db.add(new_basket_number)
    db.commit()
    db.refresh(new_basket_number)

    return new_basket_number


async def get_anonymous_user(db: Session, user_anon_id: str):
    anon_user = db.query(AnonymousUser).filter(AnonymousUser.user_anon_id == user_anon_id).first()

    if not anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return anon_user


async def get_basket_for_anonymous_user(db: Session, anon_user_id: int):
    basket_number = (
        db.query(BasketNumberAnonUser)
        .filter(BasketNumberAnonUser.anonymous_user_id == anon_user_id).first()
    )

    if not basket_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return basket_number
