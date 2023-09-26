from sqlalchemy import text
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy import inspect

from src.database.db import get_db
from src.database.models import User, Basket, Favorite


def get_table_names(models):
    table_names = []
    for model in models:
        table_names.append(model.__table__.name)
    return table_names


def clear_tables(table_names):
    session = next(get_db())

    inspector = inspect(session.get_bind())
    existing_tables = inspector.get_table_names()

    for table_name in table_names:
        if table_name in existing_tables:
            sql_query = text(f"DELETE FROM {table_name}")
            session.execute(sql_query)
            session.commit()
            print(f"Table {table_name} successfully cleared.")
        else:
            raise NoSuchTableError(f"Table {table_name} does not exist.")


if __name__ == "__main__":
    model_classes = [Basket, Favorite, User]
    table_names_to_clear = get_table_names(model_classes)

    clear_tables(table_names_to_clear)
