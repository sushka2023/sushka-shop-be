from typing import List, Tuple, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import Product, Price
from src.repository import products as repository_products
from src.repository import product_categories as repository_product_categories
from src.repository.images import images_by_product_ids
from src.repository.prices import price_by_product_ids
from src.schemas.images import ImageResponse
from src.schemas.price import PriceResponse
from src.schemas.product import ProductResponse, ProductWithPricesAndImagesResponse
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


async def product_with_price_and_images_response(products: List[Type[Product]],
                                                 prices: List[Type[PriceResponse]],
                                                 images: List[Type[ImageResponse]]) -> list:
    result = []
    for product in products:
        prices_ = []
        images_ = []
        product_response = ProductResponse(id=product.id,
                                           name=product.name,
                                           description=product.description,
                                           product_category_id=product.product_category_id,
                                           promotional=product.promotional,
                                           new_product=product.new_product,
                                           is_popular=product.is_popular,
                                           is_favorite=product.is_favorite)
        for price in prices:
            if price.product_id == product.id:
                price_response = PriceResponse(id=price.id,
                                               product_id=price.product_id,
                                               weight=price.weight,
                                               price=price.price,
                                               old_price=price.old_price,
                                               quantity=price.quantity)
                prices_.append(price_response)
        for image in images:
            if image.product_id == product.id:
                image_response = ImageResponse(id=image.id,
                                               product_id=image.product_id,
                                               image_url=image.image_url,
                                               description=image.description,
                                               image_type=image.image_type)
                images_.append(image_response)

        product_with_prices_and_img_response = ProductWithPricesAndImagesResponse(product=product_response,
                                                                                  prices=prices_,
                                                                                  images=images_)
        result.append(product_with_prices_and_img_response)

    return result


async def product_with_prices_and_images(products: list, db: Session) -> list:
    products_id = [prod.id for prod in products]
    prices_ = await price_by_product_ids(products_id, db)
    images_ = await images_by_product_ids(products_id, db)
    product_with_prices_ = await product_with_price_and_images_response(products, prices_, images_)
    return product_with_prices_
