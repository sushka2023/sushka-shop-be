from typing import List, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Product, Price
from src.repository import products as repository_products
from src.repository import product_categories as repository_product_categories
from src.repository.prices import price_by_product
from src.schemas.product import ProductResponse
from src.services.exception_detail import ExDetail as Ex


async def get_products_by_sort(sort: str, limit: int, offset: int, db: Session):
    if sort == "id":
        return await repository_products.get_products_id(limit, offset, db)
    elif sort == "name":
        return await repository_products.get_products_name(limit, offset, db)
    elif sort == "low_price":
        return await repository_products.get_products_low_price(limit, offset, db)
    elif sort == "high_price":
        return await repository_products.get_products_high_price(limit, offset, db)
    elif sort == "low_date":
        return await repository_products.get_products_low_date(limit, offset, db)
    elif sort == "high_date":
        return await repository_products.get_products_high_date(limit, offset, db)


async def get_products_by_sort_and_category_id(sort: str, limit: int, offset: int, pr_category_id: int, db: Session):
    product_category = await repository_product_categories.product_category_by_id(pr_category_id, db)
    if product_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    if sort == "id":
        return await repository_products.get_products_id_by_category_id(limit, offset, pr_category_id, db)
    elif sort == "name":
        return await repository_products.get_products_name_by_category_id(limit, offset, pr_category_id, db)
    elif sort == "low_price":
        return await repository_products.get_products_low_price_by_category_id(limit, offset, pr_category_id, db)
    elif sort == "high_price":
        return await repository_products.get_products_high_price_by_category_id(limit, offset, pr_category_id, db)
    elif sort == "low_date":
        return await repository_products.get_products_low_date_by_category_id(limit, offset, pr_category_id, db)
    elif sort == "high_date":
        return await repository_products.get_products_high_date_by_category_id(limit, offset, pr_category_id, db)


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
                                           sub_categories=product.subcategories,
                                           images=product.images,
                                           prices=await price_by_product(product, db))

        result.append(product_response)

    return result


async def product_with_prices_and_images(products: list, db: Session) -> list:
    product_with_prices_ = await product_with_price_and_images_response(products, db)
    return product_with_prices_
