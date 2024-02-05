from typing import Optional, Type
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session

from src.database.models import AnonymousUser, BasketAnonUser, BasketItemAnonUser, Product
from src.schemas.basket_anon_user import BasketItemAnonUserModel
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

    new_basket_number = BasketAnonUser(anonymous_user_id=anon_user.id)

    db.add(new_basket_number)
    db.commit()
    db.refresh(new_basket_number)

    return new_basket_number


async def get_anonymous_user_by_key_id(db: Session, user_anon_id: str):
    anon_user = db.query(AnonymousUser).filter(AnonymousUser.user_anon_id == user_anon_id).first()

    if not anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return anon_user


async def get_basket_for_anonymous_user(db: Session, user_id: int):
    basket_anon_user = (
        db.query(BasketAnonUser)
        .filter(BasketAnonUser.anonymous_user_id == user_id).first()
    )

    if not basket_anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    return basket_anon_user


async def add_items_to_basket_anon_user(
        db: Session, basket_anon_user_id: int, product_id: int, price_id_by_anon_user: int, quantity: int
):
    new_basket_item_anon_user = BasketItemAnonUser(
        basket_anon_user_id=basket_anon_user_id,
        product_id=product_id,
        quantity=quantity,
        price_id_by_anon_user=price_id_by_anon_user
    )
    db.add(new_basket_item_anon_user)
    db.commit()
    db.refresh(new_basket_item_anon_user)
    return new_basket_item_anon_user


async def get_existing_basket_anon_user(
        basket_anon_user: BasketAnonUser, product_id: int, price_id: int, db: Session
) -> Optional[BasketItemAnonUser]:
    return db.query(BasketItemAnonUser).filter(
        BasketItemAnonUser.basket_anon_user_id == basket_anon_user.id,
        BasketItemAnonUser.product_id == product_id,
        BasketItemAnonUser.price_id_by_anon_user == price_id,
    ).first()


async def update_basket_anon_user(
        body: BasketItemAnonUserModel, basket_anon_user: BasketAnonUser, db: Session
):
    existing_basket_item = (
        await get_existing_basket_anon_user(
            basket_anon_user, body.product_id, body.price_id_by_anon_user, db
        )
    )

    if existing_basket_item:
        existing_basket_item.quantity += body.quantity
        db.commit()
        db.refresh(existing_basket_item)
        return existing_basket_item


async def basket_item_anon_user(
        product_id: int,
        user_id: int,
        db: Session,
        price_id_by_anon_user: int = None
) -> Type[BasketItemAnonUser] | None:
    query = (
        db.query(BasketItemAnonUser)
        .join(BasketAnonUser)
        .filter(
            BasketItemAnonUser.product_id == product_id,
            BasketAnonUser.anonymous_user_id == user_id
        )
    )

    if price_id_by_anon_user is not None:
        query = query.filter(BasketItemAnonUser.price_id_by_anon_user == price_id_by_anon_user)

    return query.first()


async def basket_items_anon_user(user_id: int, db: Session) -> list[BasketItemAnonUser] | None:
    basket_items = (
        db.query(BasketItemAnonUser)
        .join(BasketAnonUser, BasketAnonUser.id == BasketItemAnonUser.basket_anon_user_id)
        .join(Product, Product.id == BasketItemAnonUser.product_id)
        .filter(BasketAnonUser.anonymous_user_id == user_id)
        .order_by(asc(Product.name))
        .all()
    )
    return basket_items


async def get_basket_item_by_id(
        basket_id: int, basket_item_id: int, db: Session
) -> Type[BasketItemAnonUser] | None:
    basket_item = (
        db.query(BasketItemAnonUser)
        .join(BasketAnonUser)
        .filter(
            BasketItemAnonUser.id == basket_item_id,
            BasketAnonUser.id == basket_id
        ).first()
    )

    return basket_item


async def update_quantity(
        basket_item: Type[BasketItemAnonUser], quantity: int, db: Session
) -> Type[BasketItemAnonUser] | None:
    if basket_item:
        basket_item.quantity = quantity
        db.commit()
        db.refresh(basket_item)
        return basket_item
    return None


async def get_basket_item_by_product_id_and_price_id(basket_id: int, product_id: int, price_id: int, db: Session):
    basket_item = (
        db.query(BasketItemAnonUser)
        .join(BasketAnonUser)
        .filter(
            BasketItemAnonUser.product_id == product_id,
            BasketItemAnonUser.price_id_by_anon_user == price_id,
            BasketAnonUser.id == basket_id
        ).first()
    )
    return basket_item


async def remove_item(basket_item: BasketItemAnonUser, db: Session):
    db.delete(basket_item)
    db.commit()
