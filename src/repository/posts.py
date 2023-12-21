from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload, subqueryload

from src.database.models import User, Post, post_ukrposhta_association
from src.repository.ukr_poshta import get_ukr_poshta_by_id
from src.schemas.posts import PostAddUkrPostalOffice
from src.services.exception_detail import ExDetail as Ex


async def create_postal_office(current_user: User, db: Session) -> Post:
    new_postal_office = Post(user=current_user)
    db.add(new_postal_office)
    db.commit()
    db.refresh(new_postal_office)
    return new_postal_office


async def add_ukr_postal_office_to_post(
    db: Session, ukr_poshta_in: PostAddUkrPostalOffice, user_id: int
) -> None:
    post = await get_posts_by_id_and_user_id(
        db=db, post_id=ukr_poshta_in.post_id, user_id=user_id
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    ukr_poshta_address = await get_ukr_poshta_by_id(db=db, ukr_poshta_id=ukr_poshta_in.ukr_poshta_id)

    if not ukr_poshta_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    post_ukr_post_association = post_ukrposhta_association.insert().values(
        **ukr_poshta_in.model_dump()
    )
    db.execute(post_ukr_post_association)

    db.commit()


async def get_posts_by_user_id(user_id: int, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .options(subqueryload(Post.ukr_poshta))
        .options(joinedload(Post.user))
        .filter(Post.user_id == user_id).first()
    )
    return post


async def get_posts_by_id_and_user_id(post_id: int, user_id: int, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .options(subqueryload(Post.ukr_poshta))
        .options(joinedload(Post.user))
        .filter(Post.id == post_id, Post.user_id == user_id).first()
    )
    return post


async def get_all_posts(db: Session) -> list[Post]:
    all_posts = (
        db.query(Post)
        .options(subqueryload(Post.ukr_poshta))
        .options(joinedload(Post.user))
    )
    return list(all_posts)
