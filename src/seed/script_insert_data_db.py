import os
import json

from sqlalchemy.exc import NoSuchTableError

from create_json_file import create_json_data
from src.database.db import get_db
from src.database.models import User, Basket, Favorite
from src.services.password_utils import hash_password

create_json_data()

current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir, "data.json")


def create_table_dict(*model_classes):
    table_dict = {}
    for model_class in model_classes:
        table_dict[model_class.__tablename__] = model_class.__table__
    return table_dict


TABLE_NAMES = create_table_dict(User, Basket, Favorite)


def load_data_from_json(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading of data from JSON: {str(e)}")
        return None


def insert_data_into_tables(data, tables):
    session = next(get_db())

    for table_name, items in data.items():
        table = tables.get(table_name)
        if table is None:
            raise NoSuchTableError(f"Table {table_name} not found.")

        if table_name == "users":
            for user in items:
                user["password_checksum"] = hash_password(user["password_checksum"])

        session.execute(table.insert().values(items))

    session.commit()
    print("Data inserted successfully.")


if __name__ == "__main__":
    data_json = load_data_from_json(json_file_path)

    insert_data_into_tables(data_json, TABLE_NAMES)
