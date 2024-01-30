from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import basket_anon_user as repository_basket_anon_user
from src.schemas.basket_anon_user import BasketNumberAnonUserResponse


router = APIRouter(prefix="/basket_anon_user", tags=["basket_anon_users"])


@router.post(
    "/create_basket_for_anonymous_user",
    response_model=BasketNumberAnonUserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_basket_for_anonymous_user(db: Session = Depends(get_db)):
    basket_anon_user = await repository_basket_anon_user.create_basket_for_anonymous_user(db=db)
    return basket_anon_user
