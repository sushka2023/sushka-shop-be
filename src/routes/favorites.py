from typing import List

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role, User
from src.repository import favorites as repository_favorites
from src.schemas.favorites import FavoriteResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/favorites", tags=["favorite"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post("/create",
             response_model=FavoriteResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def create(current_user: User = Depends(auth_service.get_current_user),
                 db: Session = Depends(get_db)):
    """
    The create function creates a new favorite for the current user.
        If the user already has a favorite, it will return an error.

    Args:
        current_user: User: Get the user id from the token
        db: Session: Pass the database session to the repository

    Returns:
        A favorite object
    """
    favorite = await repository_favorites.favorites(current_user, db)
    if favorite:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    new_favorite = await repository_favorites.create(current_user, db)
    return new_favorite
