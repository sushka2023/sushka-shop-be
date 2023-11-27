from typing import List, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Product, Price
from src.repository import products as repository_products
from src.repository import product_categories as repository_product_categories
from src.repository.prices import price_by_product
from src.schemas.images import ImageResponse
from src.schemas.product import ProductResponse
from src.services.cloud_image import CloudImage
from src.services.exception_detail import ExDetail as Ex


async def get_products_by_sort(sort: str, db: Session):
    if sort == "id":
        return await repository_products.get_products_id(db)
    elif sort == "name":
        return await repository_products.get_products_name(db)
    elif sort == "low_price":
        return await repository_products.get_products_low_price(db)
    elif sort == "high_price":
        return await repository_products.get_products_high_price(db)
    elif sort == "low_date":
        return await repository_products.get_products_low_date(db)
    elif sort == "high_date":
        return await repository_products.get_products_high_date(db)


async def get_products_by_sort_and_category_id(sort: str, pr_category_id: int, db: Session):
    product_category = await repository_product_categories.product_category_by_id(pr_category_id, db)
    if product_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if sort == "id":
        return await repository_products.get_products_id_by_category_id(pr_category_id, db)
    elif sort == "name":
        return await repository_products.get_products_name_by_category_id(pr_category_id, db)
    elif sort == "low_price":
        return await repository_products.get_products_low_price_by_category_id(pr_category_id, db)
    elif sort == "high_price":
        return await repository_products.get_products_high_price_by_category_id(pr_category_id, db)
    elif sort == "low_date":
        return await repository_products.get_products_low_date_by_category_id(pr_category_id, db)
    elif sort == "high_date":
        return await repository_products.get_products_high_date_by_category_id(pr_category_id, db)


async def product_with_price_and_images_response(products: List[Type[Product]], db) -> list:
    result = []
    for product in products:
        product_response = ProductResponse(id=product.id,
                                           name=product.name,
                                           description=product.description,
                                           product_category_id=product.product_category_id,
                                           promotional=product.promotional,
                                           new_product=product.new_product,
                                           is_popular=product.is_popular,
                                           is_favorite=product.is_favorite,
                                           product_status=product.product_status,
                                           sub_categories=product.subcategories,
                                           images=[ImageResponse(id=item.id,
                                                                 product_id=item.product_id,
                                                                 image_url=CloudImage.get_transformation_image(item.image_url, "product"),
                                                                 description=item.description,
                                                                 image_type=item.image_type,
                                                                 main_image=item.main_image) for item in product.images],
                                           prices=await price_by_product(product, db))

        result.append(product_response)

    return result


async def product_with_prices_and_images(products: list, db: Session) -> list:
    product_with_prices_ = await product_with_price_and_images_response(products, db)
    return product_with_prices_
