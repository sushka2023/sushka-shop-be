from typing import Type, Union

from fastapi import HTTPException, status
from sqlalchemy import desc, asc, select, exists, and_, func
from sqlalchemy.orm import Session, aliased

from src.database.models import Product, Price, ProductStatus
from src.schemas.product import ProductWithTotalResponse
from src.services.products import product_with_prices_and_images
from src.services.exception_detail import ExDetail as Ex


async def product_by_name(body: str, db: Session) -> Product | None:
    return db.query(Product).filter_by(name=body).first()


async def product_by_id(body: int, db: Session) -> Product | None:
    product = db.query(Product).filter_by(id=body).first()
    if not product:
        return None
    product_with_price = await product_with_prices_and_images([product], db)
    try:
        product_ = product_with_price[0]
    except Exception as ex:
        return None
    return product_


async def product_by_id_and_status(product_id: int, db: Session) -> Product | None:
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.product_status == ProductStatus.activated
    ).first()
    return product


async def get_products_all_for_crm(
        limit: int, offset: int, db: Session
) -> ProductWithTotalResponse | None:
    subquery = db.query(Product).\
        filter().\
        order_by(desc(Product.created_at))

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_all_for_crm_pr_category_id(
        limit: int, offset: int, pr_category_id: int, db: Session
) -> ProductWithTotalResponse | None:
    subquery = db.query(Product).\
        filter(Product.product_category_id == pr_category_id).\
        order_by(desc(Product.created_at))

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_all_for_crm_pr_status(
        limit: int, offset: int, pr_status: ProductStatus, db: Session
) -> ProductWithTotalResponse | None:
    subquery = db.query(Product).\
        filter(Product.product_status == pr_status).\
        order_by(desc(Product.created_at))

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_all_for_crm_pr_status_and_pr_category_id(
        limit: int, offset: int, pr_category_id: int, pr_status: ProductStatus, db: Session
) -> ProductWithTotalResponse | None:
    subquery = db.query(Product).\
        filter(Product.product_category_id == pr_category_id, Product.product_status == pr_status).\
        order_by(desc(Product.created_at))

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_id(limit: int, offset: int, db: Session) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Price.is_active == True
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_id_with_weight(
        limit: int, offset: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Price.is_active == True,
                Price.weight.in_(weight)
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_id_by_category_id(
        limit: int, offset: int, category_id: int, db: Session
) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Product.product_category_id == category_id,
                Price.is_active == True
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_id_by_category_id_with_weight(
        limit: int, offset: int, category_id: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Price.is_active == True,
                Price.weight.in_(weight),
                Product.product_category_id == category_id
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_name(limit: int, offset: int, db: Session) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Price.is_active == True
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(Product.name)
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_name_with_weight(
        limit: int, offset: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Price.is_active == True,
                Price.weight.in_(weight)
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(Product.name)
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_name_by_category_id(
        limit: int, offset: int, category_id: int, db: Session
) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Product.product_category_id == category_id,
                Price.is_active == True
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(Product.name)
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_name_by_category_id_with_weight(
        limit: int, offset: int, category_id: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    subquery = (
        select(1)
        .where(
            and_(
                Product.id == Price.product_id,
                Product.is_deleted == False,
                Product.product_status == ProductStatus.activated,
                Price.is_active == True,
                Price.weight.in_(weight),
                Product.product_category_id == category_id
            )
        )
        .correlate(Product)
        .limit(1)
    )

    products_ = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(Product.name)
        .limit(limit)
        .offset(offset)
        .all()
    )

    total_count = (
        db.query(Product)
        .filter(exists(subquery))
        .order_by(asc(Product.id))
        .count()
    )

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_price(
        limit: int, offset: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
        )
        .group_by(Product.id)
        .order_by(asc(func.min(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_price_with_weight(
        limit: int, offset: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated
        )
        .group_by(Product.id)
        .order_by(asc(func.min(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_price_by_category_id(
        limit: int, offset: int, category_id: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id,
        )
        .group_by(Product.id)
        .order_by(asc(func.min(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_price_by_category_id_with_weight(
        limit: int, offset: int, category_id: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id
        )
        .group_by(Product.id)
        .order_by(asc(func.min(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_price(
        limit: int, offset: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
        )
        .group_by(Product.id)
        .order_by(desc(func.max(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_price_with_weight(
        limit: int, offset: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
        )
        .group_by(Product.id)
        .order_by(desc(func.max(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_price_by_category_id(
        limit: int, offset: int, category_id: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id,
        )
        .group_by(Product.id)
        .order_by(desc(func.max(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_price_by_category_id_with_weight(
        limit: int, offset: int, category_id: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id
        )
        .group_by(Product.id)
        .order_by(desc(func.max(price_alias.price)))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_date(
        limit: int, offset: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
        )
        .group_by(Product.id)
        .order_by(asc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_date_with_weight(
        limit: int, offset: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
        )
        .group_by(Product.id)
        .order_by(asc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_date_by_category_id(
        limit: int, offset: int, category_id: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id
        )
        .group_by(Product.id)
        .order_by(asc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_low_date_by_category_id_with_weight(
        limit: int, offset: int, category_id: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id
        )
        .group_by(Product.id)
        .order_by(asc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_date(
        limit: int, offset: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
        )
        .group_by(Product.id)
        .order_by(desc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_date_with_weight(
        limit: int, offset: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
        )
        .group_by(Product.id)
        .order_by(desc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_date_by_category_id(
        limit: int, offset: int, category_id: int, db: Session
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id
        )
        .group_by(Product.id)
        .order_by(desc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def get_products_high_date_by_category_id_with_weight(
        limit: int, offset: int, category_id: int, db: Session, weight: list[str]
) -> ProductWithTotalResponse | None:
    price_alias = aliased(Price)

    subquery = (
        db.query(Product)
        .join(price_alias, and_(
            Product.id == price_alias.product_id,
            price_alias.is_active == True,
            price_alias.is_deleted == False,
            price_alias.weight.in_(weight)
        ))
        .filter(
            Product.is_deleted == False,
            Product.product_status == ProductStatus.activated,
            Product.product_category_id == category_id
        )
        .group_by(Product.id)
        .order_by(desc(Product.created_at))
    )

    products_ = subquery.limit(limit).offset(offset).all()

    total_count = subquery.count()

    product_with_price = await product_with_prices_and_images(products_, db)

    product_with_total_price = ProductWithTotalResponse(
        products=product_with_price, total_count=total_count
    )

    return product_with_total_price


async def create_product(body: dict, db: Session) -> Type[Product]:
    new_product = Product(**body)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


async def archive_product(body: int, db: Session):
    product = db.query(Product).filter_by(id=body).first()
    if product:
        product.product_status = ProductStatus.archived
        product.is_deleted = True
        db.commit()
        return product
    return None


async def unarchive_product(body: int, db: Session):
    product = db.query(Product).filter_by(id=body).first()
    if product:
        product.product_status = ProductStatus.new
        product.is_deleted = False
        db.commit()
        return product
    return None


async def get_all_products_without_filter(db: Session):
    return db.query(Product).order_by(desc(Product.created_at))


async def get_all_products_with_filter(db: Session):
    return (
        db.query(Product)
        .filter(
            Product.product_status == ProductStatus.activated,
            Product.is_deleted == False
        )
        .order_by(desc(Product.created_at))
    )


async def search_products_for_crm(
        search_query: Union[int, str], db: Session, offset: int, limit: int
) -> ProductWithTotalResponse | None:
    subquery = await get_all_products_without_filter(db=db)

    if search_query:
        if isinstance(search_query, int):
            subquery = subquery.filter_by(id=search_query)
        elif isinstance(search_query, str):
            subquery = subquery.filter(
                func.lower(Product.name).contains(func.lower(search_query))
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid search_query")

    total_count = subquery.count()

    products_ = subquery.offset(offset).limit(limit).all()

    if not products_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    products_with_price = await product_with_prices_and_images(products_, db)

    products_with_total_count = ProductWithTotalResponse(
        products=products_with_price, total_count=total_count
    )

    return products_with_total_count


async def search_all_products(
        search_query: Union[int, str], db: Session, offset: int, limit: int
) -> ProductWithTotalResponse | None:
    subquery = await get_all_products_with_filter(db=db)

    if search_query:
        if isinstance(search_query, int):
            subquery = subquery.filter_by(id=search_query)
        elif isinstance(search_query, str):
            subquery = subquery.filter(
                func.lower(Product.name).contains(func.lower(search_query))
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid search_query")

    total_count = subquery.count()

    products_ = subquery.offset(offset).limit(limit).all()

    if not products_:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    products_with_price = await product_with_prices_and_images(products_, db)

    products_with_total_count = ProductWithTotalResponse(
        products=products_with_price, total_count=total_count
    )

    return products_with_total_count
