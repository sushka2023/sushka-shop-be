from sqlalchemy.orm import Session


from src.database.models import Favorite, User


async def create(current_user: User, db: Session):
    new_favorite = Favorite(user=current_user)
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite


async def favorites(current_user: User, db: Session) -> Favorite | None:
    favorite = db.query(Favorite).filter(Favorite.user_id == current_user.id).first()
    return favorite
