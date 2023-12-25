from random import choice, choices, randint

from faker import Faker
from sqlalchemy import select, exists

from sqlalchemy.exc import NoSuchTableError
from src.database.db import get_db
from src.database.models import User, Basket, Favorite, ProductCategory, Product, ProductStatus, Post, Price
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


TABLE_NAMES = create_table_dict(User, Basket, Favorite, Post)
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
        "posts": [],
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
        data["posts"].extend(
            create_fake_post(user_id) for user_id in user_id_list
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


def create_fake_post(user_id):
    """Creating a specific post according to the user ID"""

    post = {
        "user_id": user_id,
    }
    return post


def create_product_category():
    """Creating categories of products and insert them into database"""

    categories = [
        "Пастила",
        "Фріпси",
        "Набори пастили",
        "Набори фріпсів",
    ]

    for category in categories:
        session.add(ProductCategory(name=category))
        session.commit()


def create_product_items():
    """Creating products with random value of category ID and insert them into database"""

    number_of_products = 100
    product_category_ids = session.scalars(select(ProductCategory.id)).all()

    for i in range(1, number_of_products + 1):
        product_name = f"Product {i}"
        product_description = f"Фруктова екстракухня: найсолодший смак сушених фруктів, вирощених на хмарах. Ласкаво просимо в небесний смак! #ФейкПродукт"

        session.add(
            Product(
                name=product_name,
                description=product_description,
                product_category_id=choice(product_category_ids),
                product_status=choices([ProductStatus.activated, ProductStatus.archived, ProductStatus.new], weights=[80, 10, 10])[0],
                new_product=choices([True, False], weights=[10, 90])[0],
                is_deleted=choices([True, False], weights=[5, 95])[0],
                is_popular=choices([True, False], weights=[5, 95])[0],
                is_favorite=choices([True, False], weights=[5, 95])[0],
            )
        )

    session.commit()


def create_price_item():
    """Create product price in db"""
    product_ids = session.scalars(select(Product.id)).all()
    weight = [str(50), str(100), str(150), str(200), str(300), str(400), str(500), str(1000)]
    count_price_for_product = range(1, 10)

    for i in product_ids:

        for _ in count_price_for_product:
            price = choice(weight)
            session.add(
                Price(
                    product_id=i,
                    weight=price,
                    price=float(price),
                    old_price=float(price)+100.0,
                    quantity=randint(1, 200),
                    is_deleted=choices([True, False], weights=[20, 80])[0],
                    is_active=choices([True, False], weights=[90, 10])[0],
                    promotional=choices([True, False], weights=[5, 95])[0]
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
    create_price_item()
    session.commit()
    print("Data inserted successfully.")


if __name__ == "__main__":
    fake_data = create_fake_data(num_records=num_users)

    insert_data_into_tables(fake_data, TABLE_NAMES)
