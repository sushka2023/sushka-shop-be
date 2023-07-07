from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import prices as repository_prices
from src.schemas.price import PriceResponse, PriceModel
from src.services.roles import RoleAccess

router = APIRouter(prefix="/price", tags=["price"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.post("/create_price",
             response_model=PriceResponse,
             dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_category(body: PriceModel, db: Session = Depends(get_db)):
    new_price = await repository_prices.create_price(body, db)
    return new_price
