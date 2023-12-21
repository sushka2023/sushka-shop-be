from sqlalchemy.orm import Session


from src.database.models import Basket, User


async def create(current_user: User, db: Session):
    new_basket = Basket(user=current_user)
    db.add(new_basket)
    db.commit()
    db.refresh(new_basket)
    return new_basket


async def baskets(current_user: User, db: Session) -> Basket | None:
    basket = db.query(Basket).filter(Basket.user_id == current_user.id).first()
    return basket
