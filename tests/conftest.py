import pytest
from secrets import token_hex
from sqlalchemy import create_engine, delete, insert
from users_db.config import get_postgres_uri
from users_db.schema import users


@pytest.fixture(scope="session")
def db_connection():
    engine = create_engine(get_postgres_uri())
    with engine.connect() as conn:
        yield conn


@pytest.fixture(scope="function")
def users_data(db_connection):
    users_data = [
        {
            "first_name": f"John{i}",
            "middle_name": f"E.{i}",
            "last_name": f"Doe{i}",
            "role": "USER",
            "email": f"{token_hex(4)}@example.com",
            "password": "password",
        }
        for i in range(101)
    ]

    user_ids = []
    for user_data in users_data:
        result = db_connection.execute(
            insert(users)
            .values(
                first_name=user_data["first_name"],
                middle_name=user_data["middle_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"],
            )
            .returning(users.c.id)
        )
        user_data["id"] = result.one()[0]
        user_ids.append(user_data["id"])
    db_connection.commit()

    yield users_data

    # clean up
    db_connection.execute(delete(users).where(users.c.id.in_(user_ids)))
    db_connection.commit()
