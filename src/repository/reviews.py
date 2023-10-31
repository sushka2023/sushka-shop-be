from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.database.models import Review, User
from src.schemas.reviews import ReviewModel


async def get_reviews(limit: int, offset: int, db: Session) -> list[Review]:
    return (
        db.query(Review).filter(Review.is_checked == True)
        .order_by(desc(Review.created_at)).limit(limit).offset(offset).all()
    )


async def get_reviews_for_crm(limit: int, offset: int, db: Session) -> list[Review]:
    return db.query(Review).order_by(desc(Review.created_at)).limit(limit).offset(offset).all()


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
