from typing import List

from sqlalchemy import asc
from sqlalchemy.orm import Session


from src.database.models import FavoriteItem, User, Favorite, Product
from src.schemas.favorite_items import FavoriteItemsModel


async def create(body: FavoriteItemsModel, favorite: Favorite, db: Session):
    new_favorite_item = FavoriteItem(favorite_id=favorite.id, product_id=body.product_id)
    db.add(new_favorite_item)
    db.commit()
    db.refresh(new_favorite_item)
    return new_favorite_item


async def favorite_items(current_user: User, db: Session) -> List[Favorite] | None:
    favorite_items_ = db.query(FavoriteItem.id, FavoriteItem.favorite_id, FavoriteItem.product_id) \
        .join(Favorite, Favorite.id == FavoriteItem.favorite_id) \
        .join(Product, Product.id == FavoriteItem.product_id) \
        .filter(Favorite.user_id == current_user.id) \
        .order_by(Product.name.asc()) \
        .all()
    return favorite_items_


async def favorite_item(body: FavoriteItemsModel, current_user: User, db: Session) -> Product:
    favorite_item_ = db.query(FavoriteItem.id, FavoriteItem.favorite_id, FavoriteItem.product_id) \
        .join(Favorite, Favorite.id == FavoriteItem.favorite_id) \
        .join(Product, Product.id == FavoriteItem.product_id) \
        .filter(FavoriteItem.product_id == body.product_id) \
        .order_by(Product.name.asc()) \
        .first()
    return favorite_item_
