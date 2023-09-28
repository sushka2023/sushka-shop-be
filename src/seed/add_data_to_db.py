from random import choice

from faker import Faker
from sqlalchemy import select

from sqlalchemy.exc import NoSuchTableError
from src.database.db import get_db
from src.database.models import User, Basket, Favorite, ProductCategory, Product
from src.services.password_utils import hash_password

fake = Faker()
session = next(get_db())


def create_table_dict(*model_classes):
    table_dict = {}
    for model_class in model_classes:
        table_dict[model_class.__tablename__] = model_class.__table__
    return table_dict


TABLE_NAMES = create_table_dict(User, Basket, Favorite)


def create_fake_user():
    user = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "password_checksum": hash_password(fake.password()),
        "is_active": True,
    }
    return user


def create_fake_basket(user_id):
    basket = {
        "user_id": user_id,
    }
    return basket


def create_fake_favorite(user_id):
    favorite = {
        "user_id": user_id,
    }
    return favorite


def create_product_category():

    categories = [
        "Electronics",
        "Clothes",
        "Shoes",
        "Cosmetics",
        "Furniture",
        "Sport",
        "Food products",
    ]

    for category in categories:
        session.add(ProductCategory(name=category))
        session.commit()


def create_product_items():
    number_of_products = 10
    product_category_ids = session.scalars(select(ProductCategory.id)).all()

    for i in range(1, number_of_products + 1):
        product_name = f"Product {i}"
        product_description = f"Description Product {i}"

        session.add(
            Product(
                name=product_name,
                description=product_description,
                product_category_id=choice(product_category_ids),
            )
        )

    session.commit()


def insert_user(user_data):
    user = User(**user_data)
    session.add(user)
    session.commit()
    return user.id


def create_fake_data(num_records):
    data = {
        "users": [],
        "baskets": [],
        "favorites": [],
    }

    for _ in range(num_records):
        user_data = create_fake_user()
        user_id = insert_user(user_data)
        data["users"].append(user_data)
        data["baskets"].append(create_fake_basket(user_id))
        data["favorites"].append(create_fake_favorite(user_id))

    return data


def table_has_data(table_name):
    table = TABLE_NAMES[table_name]
    return session.query(table.select().exists()).scalar()


def insert_data_into_tables(data, tables):

    for table_name, items in data.items():
        table = tables.get(table_name)
        if table is None:
            raise NoSuchTableError(f"Table {table_name} not found.")

        if table_name == "users" and table_has_data("users"):
            continue

        session.execute(table.insert().values(items))

    create_product_category()
    create_product_items()
    session.commit()
    print("Data inserted successfully.")


if __name__ == "__main__":
    fake_data = create_fake_data(num_records=3)

    insert_data_into_tables(fake_data, TABLE_NAMES)
