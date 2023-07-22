from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.repository import products as repository_products
from src.repository import product_categories as repository_product_categories
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
