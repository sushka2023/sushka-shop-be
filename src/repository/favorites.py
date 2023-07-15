from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc

from src.database.models import Favorite, User
from src.schemas.favorites import FavoriteModel


async def create(body: FavoriteModel, current_user: User, db: Session):
    new_favorite = Favorite(**body.dict())
    new_favorite.user = current_user
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite


async def favorites(current_user: User, db: Session) -> Favorite | None:
    favorites_ = db.query(Favorite).filter(Favorite.user_id == current_user.id).first()
    print()
    return favorites_
