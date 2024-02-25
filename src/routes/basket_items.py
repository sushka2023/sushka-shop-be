from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Role, User
from src.repository import basket_items as repository_basket_items
from src.repository import baskets as repository_baskets
from src.repository import products as repository_products
from src.repository import prices as repository_prices
from src.repository.products import product_by_id
from src.schemas.basket_items import (
    BasketItemsModel,
    BasketItemsResponse,
    ChangeQuantityBasketItemsModel,
    BasketItemsRemoveModel,
)
from src.schemas.images import ImageResponse
from src.schemas.product import ProductResponse
from src.services.auth import auth_service
from src.services.cloud_image import CloudImage
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex

router = APIRouter(prefix="/basket_items", tags=["basket_items"])

# role authority
allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.get("/", response_model=List[BasketItemsResponse],
            dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def basket_items(current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    The basket_items function returns a list of all the items in the basket.
        The function takes an optional user_id parameter, which is used to filter
        out only those items that belong to that particular user. If no user_id is
        provided, then all basket items are returned.

    Args:
        current_user: User: Get the current user from the database
        db: Session: Access the database

    Returns:
        A list of basket items
    """
    basket_items_ = await repository_basket_items.basket_items(current_user, db)
    if basket_items_ is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_items_with_product = list()

    for item in basket_items_:
        product = await product_by_id(item.product_id, db)

        selected_price = await repository_prices.price_by_product_id_and_price_id(
            item.product_id, item.price_id_by_the_user, db
        )

        if not selected_price:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid price_id_by_the_user")

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

        basket_items_with_product.append(BasketItemsResponse(id=item.id,
                                                             basket_id=item.basket_id,
                                                             product=exist_product,
                                                             quantity=item.quantity,
                                                             price_id_by_the_user=item.price_id_by_the_user))

    return basket_items_with_product


@router.post("/add",
             response_model=BasketItemsResponse,
             dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def add_items_to_basket(body: BasketItemsModel,
                              current_user: User = Depends(auth_service.get_current_user),
                              db: Session = Depends(get_db)):
    """
    The add_to_favorites function adds a product to the user's basket.

    Args:
        body: BasketItemsModel: Get the product_id from the request body
        current_user: User: Get the current user
        db: Session: Create a database session

    Returns:
        A basketitemsmodel object
    """
    basket = await repository_baskets.baskets(current_user, db)
    if not basket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    product = await repository_products.product_by_id_and_status(body.product_id, db)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    selected_price = await repository_prices.price_by_product_id_and_price_id(
        body.product_id, body.price_id_by_the_user, db
    )

    if not selected_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid price_id_by_the_user")

    basket_item = await repository_basket_items.basket_item(
        body, current_user, db, selected_price.id,
    )

    add_product_to_basket = None

    if basket_item:
        add_product_to_basket = await repository_basket_items.update(body, basket, db)
    elif not basket_item:
        add_product_to_basket = await repository_basket_items.create(
            db=db,
            basket_id=basket.id,
            product_id=body.product_id,
            quantity=body.quantity,
            price_id_by_the_user=body.price_id_by_the_user,
        )

    basket_items_with_product = list()

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

        add_product_to_basket = BasketItemsResponse(id=add_product_to_basket.id,
                                                    basket_id=add_product_to_basket.basket_id,
                                                    product=exist_product,
                                                    quantity=add_product_to_basket.quantity,
                                                    price_id_by_the_user=selected_price.id)
        return add_product_to_basket

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)


@router.delete("/remove",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def remove_product(body: BasketItemsRemoveModel,
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The remove_product function removes a product from the basket.
        The function takes in a body of type BasketItemsRemoveModel, which contains the id of the product to be removed.
        It also takes in an optional current_user parameter, which is used to identify whose basket we are removing from.
        Finally, it takes in an optional db parameter, which is used for database access.

    Args:
        body: BasketItemsRemoveModel: Get the product_id from the request body
        current_user: User: Get the current user
        db: Session: Get a database session

    Returns:
        None
    """
    basket = await repository_baskets.baskets(current_user, db)
    if not basket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    basket_item = await repository_basket_items.basket_item_for_id(body.id, db)
    if not basket_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    await repository_basket_items.remove(basket_item, db)  # Remove product from basket


@router.patch("/quantity",
              response_model=BasketItemsResponse,
              dependencies=[Depends(allowed_operation_admin_moderator_user)])
async def change_quantity_items_to_basket(body: ChangeQuantityBasketItemsModel,
                                          db: Session = Depends(get_db)):

    basket_item = await repository_basket_items.basket_item_for_id(body.id, db)

    if not basket_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    update_quantity_basket_item = await repository_basket_items.update_quantity(basket_item, body.quantity, db)

    product = await product_by_id(basket_item.product_id, db)

    update_quantity_basket_item = BasketItemsResponse(id=update_quantity_basket_item.id,
                                                      basket_id=update_quantity_basket_item.basket_id,
                                                      product=product,
                                                      quantity=update_quantity_basket_item.quantity,
                                                      price_id_by_the_user=update_quantity_basket_item.price_id_by_the_user)

    return update_quantity_basket_item
