from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role
from src.repository import prices as repository_prices
from src.repository import products as repository_products
from src.schemas.price import PriceResponse, PriceModel, PriceArchiveModel
from src.services.roles import RoleAccess

router = APIRouter(prefix="/favorites", tags=["price"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])