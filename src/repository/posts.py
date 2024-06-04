from fastapi import HTTPException, status

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload, subqueryload

from src.database.models import (
    User,
    Post,
    NovaPoshta,
    UkrPoshta,
    post_ukrposhta_association,
    post_novaposhta_association,
)

from src.repository.nova_poshta import get_nova_poshta_by_id
from src.repository.ukr_poshta import get_ukr_poshta_by_id

from src.schemas.nova_poshta import NovaPoshtaAddressDeliveryCreate
from src.schemas.posts import PostUkrPostalOffice, PostNovaPoshtaOffice
from src.schemas.ukr_poshta import UkrPoshtaCreate

from src.services.exception_detail import ExDetail as Ex


async def create_postal_office(current_user: User, db: Session) -> Post:
    new_postal_office = Post(user=current_user)
    db.add(new_postal_office)
    db.commit()
    db.refresh(new_postal_office)
    return new_postal_office


async def get_posts_by_user_id(user_id: int, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .options(subqueryload(Post.ukr_poshta))
        .options(subqueryload(Post.nova_poshta))
        .options(joinedload(Post.user))
        .filter(Post.user_id == user_id).first()
    )
    return post


async def get_posts_by_id_and_user_id(post_id: int, user_id: int, db: Session) -> Post | None:
    post = (
        db.query(Post)
        .options(subqueryload(Post.ukr_poshta))
        .options(subqueryload(Post.nova_poshta))
        .options(joinedload(Post.user))
        .filter(Post.id == post_id, Post.user_id == user_id).first()
    )
    return post


async def add_nova_poshta_warehouse_to_post_for_current_user(
    db: Session, nova_poshta_in: PostNovaPoshtaOffice, user_id: int,
) -> None:
    post = await get_posts_by_id_and_user_id(
        db=db, post_id=nova_poshta_in.post_id, user_id=user_id
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    nova_poshta_data = await get_nova_poshta_by_id(db=db, nova_poshta_id=nova_poshta_in.nova_poshta_id)

    if not nova_poshta_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    post_nova_post_association = post_novaposhta_association.insert().values(
        **nova_poshta_in.dict()
    )
    db.execute(post_nova_post_association)

    db.commit()


async def create_nova_poshta_address_delivery_and_associate_with_post(
    nova_post_address_delivery: NovaPoshtaAddressDeliveryCreate, user_id: int, post_id: int, db: Session,
) -> NovaPoshta:
    new_nova_poshta_address_delivery = NovaPoshta(**nova_post_address_delivery.dict())
    new_nova_poshta_address_delivery.is_delivery = True
    db.add(new_nova_poshta_address_delivery)
    db.commit()
    db.refresh(new_nova_poshta_address_delivery)

    post = await get_posts_by_id_and_user_id(
        db=db, post_id=post_id, user_id=user_id
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    post_nova_post_association = post_novaposhta_association.insert().values(
        post_id=post.id, nova_poshta_id=new_nova_poshta_address_delivery.id
    )
    db.execute(post_nova_post_association)

    db.commit()

    return new_nova_poshta_address_delivery


async def create_ukr_poshta_and_associate_with_post(
    db: Session, ukr_postal_office: UkrPoshtaCreate, user_id: int, post_id: int
) -> UkrPoshta:
    new_ukr_poshta_office = UkrPoshta(**ukr_postal_office.dict())
    db.add(new_ukr_poshta_office)
    db.commit()
    db.refresh(new_ukr_poshta_office)

    post = await get_posts_by_id_and_user_id(
        db=db, post_id=post_id, user_id=user_id
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    post_ukr_post_association = post_ukrposhta_association.insert().values(
        post_id=post.id, ukr_poshta_id=new_ukr_poshta_office.id
    )
    db.execute(post_ukr_post_association)

    db.commit()

    return new_ukr_poshta_office


async def remove_ukr_postal_office_from_post(
    db: Session, ukr_poshta_in: PostUkrPostalOffice, user_id: int, post_id: int
) -> None:

    post = await get_posts_by_id_and_user_id(
        db=db, post_id=post_id, user_id=user_id
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    ukr_poshta_address = await get_ukr_poshta_by_id(db=db, ukr_poshta_id=ukr_poshta_in.ukr_poshta_id)

    if not ukr_poshta_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    association_record = (
        db.query(post_ukrposhta_association)
        .filter(
            post_ukrposhta_association.c.post_id == post.id,
            post_ukrposhta_association.c.ukr_poshta_id == ukr_poshta_address.id
        )
        .first()
    )

    if not association_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    post_ukr_post_association = post_ukrposhta_association.delete().where(
        and_(
            post_ukrposhta_association.c.post_id == post.id,
            post_ukrposhta_association.c.ukr_poshta_id == ukr_poshta_address.id
        )
    )
    db.execute(post_ukr_post_association)

    db.commit()

    other_associations = (
        db.query(post_ukrposhta_association)
        .filter(post_ukrposhta_association.c.ukr_poshta_id == ukr_poshta_address.id)
        .all()
    )

    if not other_associations:
        db.delete(ukr_poshta_address)
        db.commit()


async def remove_nova_postal_data_from_post(
    db: Session, nova_poshta_in: PostNovaPoshtaOffice, user_id: int
) -> None:

    post = await get_posts_by_id_and_user_id(
        db=db, post_id=nova_poshta_in.post_id, user_id=user_id
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    nova_poshta_data = await get_nova_poshta_by_id(db=db, nova_poshta_id=nova_poshta_in.nova_poshta_id)

    if not nova_poshta_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    association_record = (
        db.query(post_novaposhta_association)
        .filter(
            post_novaposhta_association.c.post_id == post.id,
            post_novaposhta_association.c.nova_poshta_id == nova_poshta_data.id
        )
        .first()
    )

    if not association_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    post_nova_post_association = post_novaposhta_association.delete().where(
        and_(
            post_novaposhta_association.c.post_id == post.id,
            post_novaposhta_association.c.nova_poshta_id == nova_poshta_data.id
        )
    )
    db.execute(post_nova_post_association)

    db.commit()

    other_associations = (
        db.query(post_novaposhta_association)
        .filter(post_novaposhta_association.c.nova_poshta_id == nova_poshta_data.id)
        .all()
    )

    if not other_associations and nova_poshta_data.is_delivery == True:
        db.delete(nova_poshta_data)
        db.commit()
