from random import choice

from faker import Faker
from sqlalchemy import select, exists

from sqlalchemy.exc import NoSuchTableError
from src.database.db import get_db
from src.database.models import User, Basket, Favorite, ProductCategory, Product
from src.seed.test_users_data import USERS_DATA
from src.services.password_utils import hash_password


fake = Faker()
session = next(get_db())


def create_table_dict(*model_classes):
    """Creating the dictionary of table names"""

    table_dict = {}
    for model_class in model_classes:
        table_dict[model_class.__tablename__] = model_class.__table__
    return table_dict


TABLE_NAMES = create_table_dict(User, Basket, Favorite)
num_users = len(USERS_DATA)


def create_fake_users(num_users):
    """Creating a user list from specific user data and data created with Faker"""

    fake_users = []

    for _ in range(num_users):
        real_user_data = USERS_DATA[_ % num_users]
        email = real_user_data["email"]

        user_exists = session.query(exists().where(User.email == email)).scalar()

        if not user_exists:
            user = {
                "email": email,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "password_checksum": hash_password(real_user_data["password"]),
                "is_active": True,
                "role": real_user_data["role"],
            }
            fake_users.append(user)
    return fake_users


def create_fake_data(num_records):
    """Combining dependent data of models before adding them to the database"""

    data = {
        "users": [],
        "baskets": [],
        "favorites": [],
    }

    for _ in range(num_records):
        fake_users = create_fake_users(num_users)
        user_id_list = []

        for user_item in fake_users:
            user_id = insert_user(user_item)
            user_id_list.append(user_id)
            data["users"].extend(user_item)

        data["baskets"].extend(create_fake_basket(user_id) for user_id in user_id_list)
        data["favorites"].extend(
            create_fake_favorite(user_id) for user_id in user_id_list
        )

    return data


def create_fake_basket(user_id):
    """Creating a specific basket according to the user ID"""

    basket = {
        "user_id": user_id,
    }
    return basket


def create_fake_favorite(user_id):
    """Creating a specific favorite according to the user ID"""

    favorite = {
        "user_id": user_id,
    }
    return favorite


def create_product_category():
    """Creating categories of products and insert them into database"""

    categories = [
        "Marshmallow",
        "Pastille",
        "Phrypse",
        "Sets",
    ]

    for category in categories:
        session.add(ProductCategory(name=category))
        session.commit()


def create_product_items():
    """Creating products with random value of category ID and insert them into database"""

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
    """Insert user data into database"""

    user = User(**user_data)
    session.add(user)
    session.commit()
    return user.id


def table_has_data(table_name):
    """Checking tables for data existing"""

    table = TABLE_NAMES[table_name]
    return session.query(table.select().exists()).scalar()


def insert_data_into_tables(data, tables):
    """Insert data all models into database"""

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
    fake_data = create_fake_data(num_records=num_users)

    insert_data_into_tables(fake_data, TABLE_NAMES)
