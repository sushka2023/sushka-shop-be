from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.database.models import User, Image, ImageType
from src.schemas.images import ImageModel


async def get_images(limit: int, offset: int, user: User, db: Session) -> List[Image] | List:
    images = db.query(Image).filter(and_(Image.user_id == user.id, Image.is_deleted == False)).\
        order_by(desc(Image.created_at)).limit(limit).offset(offset).all()
    return images


async def get_image(image_id: int, user: User, db: Session) -> Image | None:
    image = db.query(Image).filter(and_(Image.user_id == user.id, Image.id == image_id, Image.is_deleted == False)).\
        order_by(desc(Image.created_at)).first()
    return image


async def create(body: ImageModel, image_url: str, db: Session) -> Image:
    image = Image(description=body.description, image_url=image_url, image_type=ImageType.product)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


async def get_image_from_id(image_id: int, user: User, db: Session) -> Image | None:
    image = db.query(Image).filter(and_(Image.id == image_id, Image.user_id == user.id, Image.is_deleted == False)).first()
    return image


async def get_image_from_url(image_url: str, user: User, db: Session) -> Image | None:
    image = db.query(Image).filter(and_(Image.image_url == image_url,
                                        Image.user_id == user.id,
                                        Image.is_deleted == False)).first()
    return image


async def remove(image_id: int, user: User, db: Session) -> Image | None:
    image = await get_image_from_id(image_id, user, db)
    if image:
        image.is_deleted = True
        db.commit()
    return image


async def change_description(body: ImageModel, image_id: int, user: User, db: Session) -> Image | None:
    image = await get_image_from_id(image_id, user, db)
    if image:
        image.description = body.description
        db.commit()
    return image
