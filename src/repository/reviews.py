from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from src.database.models import Review, User
from src.schemas.reviews import ReviewModel


async def get_reviews(limit: int, offset: int, db: Session) -> list[Review]:
    return (
        db.query(Review).filter(and_(Review.is_checked == True, Review.is_deleted == False))
        .order_by(desc(Review.rate), desc(Review.created_at)).limit(limit).offset(offset).all()
    )


async def get_reviews_for_crm(limit: int, offset: int, db: Session) -> list[Review]:
    return db.query(Review).order_by(Review.is_deleted, desc(Review.created_at)).limit(limit).offset(offset).all()


async def get_review_for_product_by_user(db: Session, product_id: int, user_id: int) -> Review:
    """
    Function takes a user_id, product_id and a database session,
    and returns the review with that data.

    Args:
        db(Session): SQLAlchemy session object for accessing the database
        product_id: Pass the id of the product to which the review was added
        user_id: Pass in the id of the user who created the review

    Returns:
        Review which created to the product by current user
    """
    review = db.query(Review).filter(
        Review.product_id == product_id, Review.user_id == user_id
    ).first()
    return review


async def get_review_by_id(review_id: int, db: Session) -> Review | None:
    return db.query(Review).filter_by(id=review_id).first()


async def create_review(review: ReviewModel, db: Session, user: User) -> Review:
    """
       Function creates a new review.

       Arguments:
           review (ReviewModel): object with review data
           user (User): the current user
           db (Session): SQLAlchemy session object for accessing the database

       Returns:
           Review: a new review which created to the product by current user
       """

    new_review = Review(
        product_id=review.product_id,
        user_id=user.id,
        rate=review.rate,
        description=review.description,
        image_id=review.image_id if review.image_id else None,
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


async def archive_review(review_id: int, db: Session) -> Review | None:
    review = await get_review_by_id(review_id=review_id, db=db)
    if review:
        review.is_deleted = True
        db.commit()
        return review
    return None


async def unarchive_review(review_id: int, db: Session) -> Review | None:
    review = await get_review_by_id(review_id=review_id, db=db)
    if review:
        review.is_deleted = False
        db.commit()
        return review
    return None


async def check_review(review_id: int, db: Session) -> Review | None:
    review = await get_review_by_id(review_id=review_id, db=db)
    if review and review.is_checked is False:
        review.is_checked = True
        db.commit()
        return review
    return None
