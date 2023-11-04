import pickle

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.caching import get_redis
from src.database.db import get_db
from src.database.models import User, Role
from src.repository import reviews as repository_reviews
from src.schemas.reviews import ReviewResponse, ReviewModel, ReviewArchiveModel, ReviewCheckModel
from src.services.auth import auth_service
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex


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
    redis_client = get_redis()

    key = "reviews"

    cached_reviews = None

    if redis_client:
        cached_reviews = redis_client.get(key)

    if not cached_reviews:
        reviews = await repository_reviews.get_reviews(limit, offset, db)

        if redis_client:
            redis_client.set(key, pickle.dumps(reviews))
            redis_client.expire(key, 1800)
    else:
        reviews = pickle.loads(cached_reviews)

    return reviews


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
            status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT
        )

    new_review = await repository_reviews.create_review(review, db, current_user)

    await delete_cache_in_redis()

    return new_review


@router.put("/check_review",
            response_model=ReviewResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def check_review(review: ReviewCheckModel, db: Session = Depends(get_db)):
    """
    The check_review function checks a review.

    Args:
        review: ReviewCheckModel: Get the id of the review to check and changed status of field is_checked
        db: Session: Access the database

    Returns:
        A review checked model object
    """
    review = await repository_reviews.get_review_by_id(review.id, db)

    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if review.is_checked:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)

    check_review_ = await repository_reviews.check_review(review.id, db)

    return check_review_


@router.put("/archive",
            response_model=ReviewResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def archive_review(review: ReviewArchiveModel, db: Session = Depends(get_db)):
    """
    The archive_review function is used to archive a review.
        The function takes in the id of the review to be archived and returns an object containing information about
        the archived review.

    Args:
        review: ReviewArchiveModel: Get the id of the review to be archived
        db: Session: Access the database

    Returns:
        A review archive model object
    """
    review = await repository_reviews.get_review_by_id(review.id, db)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if review.is_deleted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    archive_review_ = await repository_reviews.archive_review(review.id, db)

    await delete_cache_in_redis()

    return archive_review_


@router.put("/unarchive",
            response_model=ReviewResponse,
            dependencies=[Depends(allowed_operation_admin_moderator)])
async def unarchive_review(review: ReviewArchiveModel, db: Session = Depends(get_db)):
    """
    The unarchive_review function is used to unarchive a review.
        The function takes in the id of the review and returns an object containing information about that review.

    Args:
        review: ReviewArchiveModel: Get the id of the review to be unarchived
        db: Session: Access the database

    Returns:
        A review unarchive model object
    """
    review = await repository_reviews.get_review_by_id(review.id, db)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)
    if review.is_deleted is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Ex.HTTP_409_CONFLICT)
    return_archive_review = await repository_reviews.unarchive_review(review.id, db)

    await delete_cache_in_redis()

    return return_archive_review
