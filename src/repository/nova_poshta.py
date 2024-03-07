from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import NovaPoshta, post_novaposhta_association, Post, User
from src.services.exception_detail import ExDetail as Ex


async def get_nova_poshta_by_id(nova_poshta_id: int, db: Session) -> NovaPoshta | None:
    return db.query(NovaPoshta).filter_by(id=nova_poshta_id).first()


async def update_nova_poshta_data(
    db: Session, nova_poshta_id: int, nova_poshta_data: dict
) -> NovaPoshta:

    updated_data_nova_poshta = await get_nova_poshta_by_id(nova_poshta_id=nova_poshta_id, db=db)

    if not updated_data_nova_poshta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if updated_data_nova_poshta.address_warehouse:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Ex.HTTP_400_BAD_REQUEST)

    updated_data_nova_poshta.update_from_dict(nova_poshta_data)

    db.commit()
    db.refresh(updated_data_nova_poshta)

    return updated_data_nova_poshta


async def get_nova_poshta_warehouse(nova_poshta_id: int, user_id: int, db: Session):
    nova_poshta_warehouse = (
        db.query(NovaPoshta)
        .join(post_novaposhta_association)
        .join(Post)
        .join(User)
        .filter(
            NovaPoshta.is_delivery == False,
            NovaPoshta.id == nova_poshta_id,
            post_novaposhta_association.c.post_id == Post.id,
            Post.user_id == user_id
        )
        .first()
    )

    return nova_poshta_warehouse


async def get_nova_poshta_address_delivery(nova_poshta_id: int, user_id: int, db: Session):
    nova_poshta_address = (
        db.query(NovaPoshta)
        .join(post_novaposhta_association)
        .join(Post)
        .filter(
            NovaPoshta.is_delivery == True,
            NovaPoshta.id == nova_poshta_id,
            post_novaposhta_association.c.post_id == Post.id,
            Post.user_id == user_id
        )
        .first()
    )

    return nova_poshta_address
