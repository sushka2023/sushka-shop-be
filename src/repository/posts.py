from sqlalchemy.orm import Session, joinedload

from src.database.models import User, Post
from src.schemas.posts import PostAddUkrPostalOffice


async def create_postal_office(current_user: User, db: Session) -> Post:
    new_postal_office = Post(user=current_user)
    db.add(new_postal_office)
    db.commit()
    db.refresh(new_postal_office)
    return new_postal_office


async def add_ukr_postal_office_to_post(
        update_post: PostAddUkrPostalOffice, post_id: int, user_id: int, db: Session
) -> Post:
    updated_post = await get_posts_by_id_and_user_id(post_id, user_id, db)

    if updated_post:
        updated_post.ukr_poshta_id = update_post.ukr_poshta_id
        db.commit()
        db.refresh(updated_post)
        return updated_post


async def get_posts_by_user_id(user_id: int, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .options(joinedload(Post.ukr_poshta))
        .options(joinedload(Post.user))
        .filter(Post.user_id == user_id).first()
    )
    return post


async def get_posts_by_id_and_user_id(post_id: int, user_id: int, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .options(joinedload(Post.ukr_poshta))
        .options(joinedload(Post.user))
        .filter(Post.id == post_id, Post.user_id == user_id).first()
    )
    return post


async def get_all_posts(db: Session) -> list[Post]:
    all_posts = (
        db.query(Post)
        .options(joinedload(Post.ukr_poshta))
        .options(joinedload(Post.user))
    )
    return list(all_posts)
