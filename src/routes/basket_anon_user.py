from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import products as repository_products
from src.repository import prices as repository_prices
from src.repository import basket_anon_user as repository_basket_anon_user
from src.repository.products import product_by_id
from src.schemas.basket_anon_user import (
    BasketNumberAnonUserResponse,
    BasketAnonUserModel,
    BasketAnonUserResponse,
    ChangeQuantityBasketItemModel,
    BasketAnonUserRemoveModel,
    BasketAnonUserMessage,
)
from src.schemas.images import ImageResponse
from src.schemas.product import ProductResponse
from src.services.cloud_image import CloudImage
from src.services.exception_detail import ExDetail as Ex


router = APIRouter(prefix="/basket_anon_user", tags=["basket_anon_users"])


@router.post(
    "/create_basket_for_anonymous_user",
    response_model=BasketNumberAnonUserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_basket_for_anonymous_user(db: Session = Depends(get_db)):
    basket_anon_user = await repository_basket_anon_user.create_basket_for_anonymous_user(db=db)
    return basket_anon_user


@router.post(
    "/add_items", response_model=BasketAnonUserResponse, status_code=status.HTTP_201_CREATED
)
async def add_items_to_basket_for_anon_user(
        body: BasketAnonUserModel, user_anon_id: str = Header(...), db: Session = Depends(get_db)
):
    """
    The add_items_to_basket_for_anon_user function adds a product to the anonym user's basket.

    Args:
        user_anon_id: AnonymousUser: unique identity data of anonym user
        body: BasketAnonUserModel: Get the product_id from the request body
        db: Session: Create a database session

    Returns:
        A basketanonusermodel object
    """
    anon_user = await repository_basket_anon_user.get_anonymous_user_by_key_id(db=db, user_anon_id=user_anon_id)

    if not anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_number = await repository_basket_anon_user.get_basket_for_anonymous_user(db, anon_user.id)

    if not basket_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    product = await repository_products.product_by_id(body.product_id, db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    selected_price = await repository_prices.price_by_product_id_and_price_id(
        body.product_id, body.price_id_by_anon_user, db
    )

    if not selected_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid price_id_by_anon_user"
        )

    basket_item_anon_user = await repository_basket_anon_user.basket_item_anon_user(
        body.product_id, anon_user.id, db, selected_price.id,
    )

    add_product_to_basket = None

    if basket_item_anon_user:
        add_product_to_basket = await repository_basket_anon_user.update_basket_anon_user(body, basket_number, db)
    elif not basket_item_anon_user:
        add_product_to_basket = await repository_basket_anon_user.add_items_to_basket_anon_user(
            db=db,
            product_id=body.product_id,
            basket_number_id=basket_number.id,
            price_id_by_anon_user=body.price_id_by_anon_user,
            quantity=body.quantity,
        )

    if add_product_to_basket:
        product = await product_by_id(add_product_to_basket.product_id, db)

        exist_product = ProductResponse(id=product.id,
                                        name=product.name,
                                        description=product.description,
                                        product_category_id=product.product_category_id,
                                        new_product=product.new_product,
                                        is_popular=product.is_popular,
                                        is_favorite=product.is_favorite,
                                        product_status=product.product_status,
                                        sub_categories=product.sub_categories,
                                        images=[ImageResponse(id=item.id,
                                                              product_id=item.product_id,
                                                              image_url=CloudImage.get_transformation_image(
                                                                  item.image_url, "product"
                                                              ),
                                                              description=item.description,
                                                              image_type=item.image_type,
                                                              main_image=item.main_image) for item in product.images],
                                        prices=[selected_price])

        add_product_to_basket = BasketAnonUserResponse(id=add_product_to_basket.id,
                                                       basket_number_id=add_product_to_basket.basket_number_id,
                                                       product_id=add_product_to_basket.product_id,
                                                       product=exist_product,
                                                       quantity=add_product_to_basket.quantity,
                                                       price_id_by_anon_user=selected_price.id)

        return add_product_to_basket

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)


@router.get("/", response_model=list[BasketAnonUserResponse])
async def basket_items_anon_user(user_anon_id: str = Header(...), db: Session = Depends(get_db)):
    """
    The basket_items_anon_user function returns a list of all the items in the basket.

    Args:
        user_anon_id: AnonymousUser: unique identity data of anonym user
        db: Session: Access the database

    Returns:
        A list of basket items
    """
    anon_user = await repository_basket_anon_user.get_anonymous_user_by_key_id(db=db, user_anon_id=user_anon_id)

    if not anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_items = await repository_basket_anon_user.basket_items_anon_user(anon_user.id, db)
    if basket_items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_items_with_product = list()

    for item in basket_items:
        product = await product_by_id(item.product_id, db)

        selected_price = await repository_prices.price_by_product_id_and_price_id(
            item.product_id, item.price_id_by_anon_user, db
        )

        if not selected_price:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid price_id_by_anon_user")

        exist_product = ProductResponse(id=product.id,
                                        name=product.name,
                                        description=product.description,
                                        product_category_id=product.product_category_id,
                                        new_product=product.new_product,
                                        is_popular=product.is_popular,
                                        is_favorite=product.is_favorite,
                                        product_status=product.product_status,
                                        sub_categories=product.sub_categories,
                                        images=[ImageResponse(id=item.id,
                                                              product_id=item.product_id,
                                                              image_url=CloudImage.get_transformation_image(
                                                                  item.image_url, "product"
                                                              ),
                                                              description=item.description,
                                                              image_type=item.image_type,
                                                              main_image=item.main_image) for item in product.images],
                                        prices=[selected_price])

        basket_items_with_product.append(BasketAnonUserResponse(id=item.id,
                                                                basket_number_id=item.basket_number_id,
                                                                product_id=item.product_id,
                                                                product=exist_product,
                                                                quantity=item.quantity,
                                                                price_id_by_anon_user=item.price_id_by_anon_user))

    return basket_items_with_product


@router.patch("/change_quantity", response_model=BasketAnonUserResponse)
async def change_quantity_items_to_basket(
        body: ChangeQuantityBasketItemModel,
        user_anon_id: str = Header(...),
        db: Session = Depends(get_db)
):
    anon_user = await repository_basket_anon_user.get_anonymous_user_by_key_id(db=db, user_anon_id=user_anon_id)

    if not anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_number = await repository_basket_anon_user.get_basket_for_anonymous_user(db, anon_user.id)

    if not basket_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_item = await repository_basket_anon_user.get_basket_item_by_id(basket_number.id, body.id, db)

    if not basket_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    selected_price = await repository_prices.price_by_product_id_and_price_id(
        basket_item.product_id, basket_item.price_id_by_anon_user, db
    )

    if not selected_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid price_id_by_anon_user")

    update_quantity_basket_item = await repository_basket_anon_user.update_quantity(basket_item, body.quantity, db)

    product = await product_by_id(basket_item.product_id, db)

    exist_product = ProductResponse(id=product.id,
                                    name=product.name,
                                    description=product.description,
                                    product_category_id=product.product_category_id,
                                    new_product=product.new_product,
                                    is_popular=product.is_popular,
                                    is_favorite=product.is_favorite,
                                    product_status=product.product_status,
                                    sub_categories=product.sub_categories,
                                    images=[ImageResponse(id=item.id,
                                                          product_id=item.product_id,
                                                          image_url=CloudImage.get_transformation_image(
                                                              item.image_url, "product"
                                                          ),
                                                          description=item.description,
                                                          image_type=item.image_type,
                                                          main_image=item.main_image) for item in product.images],
                                    prices=[selected_price])

    update_quantity_basket_item = BasketAnonUserResponse(id=update_quantity_basket_item.id,
                                                         basket_number_id=(
                                                             update_quantity_basket_item.basket_number_id
                                                         ),
                                                         product_id=update_quantity_basket_item.product_id,
                                                         product=exist_product,
                                                         quantity=update_quantity_basket_item.quantity,
                                                         price_id_by_anon_user=(
                                                             update_quantity_basket_item.price_id_by_anon_user)
                                                         )

    return update_quantity_basket_item


@router.delete("/remove_product", response_model=BasketAnonUserMessage)
async def remove_product(
        body: BasketAnonUserRemoveModel,
        user_anon_id: str = Header(...),
        db: Session = Depends(get_db)
):
    """
    The remove_product function removes a product from the basket.
        The function takes in a body of type BasketItemsRemoveModel, which contains the id of the product to be removed.
        Finally, it takes in an optional db parameter, which is used for database access.

    Args:
        user_anon_id: AnonymousUser: unique identity data of anonym user
        body: BasketAnonUserRemoveModel: Get the product_id from the request body
        db: Session: Get a database session

    Returns:
        Message about successfully deleting of product from basket
    """
    anon_user = await repository_basket_anon_user.get_anonymous_user_by_key_id(db=db, user_anon_id=user_anon_id)

    if not anon_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_number = await repository_basket_anon_user.get_basket_for_anonymous_user(db, anon_user.id)

    if not basket_number:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    product = await product_by_id(body.product_id, db)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_item = await repository_basket_anon_user.basket_item_anon_user(product.id, anon_user.id, db)

    if not basket_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    product_from_basket = (
        await repository_basket_anon_user.get_basket_item_by_product_id(
            basket_number.id, body.product_id, db
        )
    )

    await repository_basket_anon_user.remove_item(product_from_basket, db)

    return {"message": "Product removed successfully"}
