from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import reviews as repository_reviews
from src.schemas.reviews import ReviewResponse, ReviewModel
from src.services.auth import auth_service
from src.services.roles import RoleAccess


router = APIRouter(prefix="/reviews", tags=["reviews"])

allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=list[ReviewResponse])
async def get_reviews(limit: int, offset: int, db: Session = Depends(get_db)):
    """
    The function returns a list of all reviews in the database which were checked by an admin or a moderator.

    Args:
        limit: int: Limit the number of reviews returned
        offset: int: Specify the offset of the first review to be returned
        db: Session: Access the database

    Returns:
        A list of reviews
    """
    return await repository_reviews.get_reviews(limit, offset, db)


@router.get("/all_for_crm", response_model=list[ReviewResponse],
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def get_reviews_for_crm(limit: int, offset: int, db: Session = Depends(get_db)):
    """
    The function returns a list of all reviews in the database.

    Args:
        limit: int: Limit the number of reviews returned
        offset: int: Specify the offset of the first review to be returned
        db: Session: Access the database

    Returns:
        A list of reviews
    """
    return await repository_reviews.get_reviews_for_crm(limit, offset, db)


@router.post("/create",
             response_model=ReviewResponse,
             status_code=status.HTTP_201_CREATED)
async def create_review(
        review: ReviewModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The create_review function creates a new review to product in the database.

    Args:
        review: ReviewModel: Validate the request body
        db: Session: Pass the database session to the repository layer
        current_user (User): the current user attempting to create the review

    Returns:
        A review object
    """

    existing_review = await repository_reviews.get_review_for_product_by_user(db, review.product_id, current_user.id)

    if existing_review:
        raise HTTPException(
            status_code=400, detail="Your review to this product already exists"
        )

    new_review = await repository_reviews.create_review(review, db, current_user)

    return new_review
