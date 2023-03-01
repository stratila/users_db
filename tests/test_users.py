import pytest

from sqlalchemy import create_engine, select, delete

from users_db.config import get_postgres_uri
from users_db.schema import users
from users_db.users import create_user, get_user, get_users, update_user, delete_user


@pytest.fixture(scope="session")
def db_connection():
    engine = create_engine(get_postgres_uri())
    with engine.connect() as conn:
        yield conn


def test_create_user(db_connection):
    first_name = "John"
    middle_name = None
    last_name = "Doe"
    user_id = create_user(
        first_name=first_name, middle_name=middle_name, last_name=last_name
    )

    result = (
        db_connection.execute(select(users).where(users.c.id == user_id))
        .mappings()
        .one()
    )
    assert result["id"] == user_id
    assert result["first_name"] == first_name
    assert result["last_name"] == last_name
    assert result["middle_name"] == middle_name

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_get_user(db_connection):
    user_data = {"first_name": "John", "middle_name": "E.", "last_name": "Doe"}

    user_id = create_user(**user_data)
    user = get_user(user_id)

    assert user["id"] == user_id
    for key in user_data.keys():
        assert user[key] == user_data[key]

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_get_users(db_connection):
    users_data = [
        {"first_name": "John", "middle_name": "E.", "last_name": "Doe"},
        {"first_name": "Madeline", "middle_name": "J.", "last_name": "Doe"},
    ]

    user_ids = []
    for user_data in users_data:
        user_data["id"] = create_user(**user_data)
        user_ids.append(user_data["id"])

    users_ = get_users(user_ids=user_ids)

    for user in users_:
        for user_data in users_data:
            if user["id"] == user_data["id"]:
                for key in user_data.keys():
                    assert user[key] == user_data[key]

    # clean up
    for user_id in user_ids:
        db_connection.execute(delete(users).where(users.c.id == user_id))
        db_connection.commit()


def test_update_users(db_connection):
    user_data = {"first_name": "John", "middle_name": "E.", "last_name": "Doe"}
    update_user_data = {"middle_name": "Emmanuel"}
    user_id = create_user(**user_data)
    updated_user_id = update_user(user_id, **update_user_data)
    assert user_id == updated_user_id
    updated_user = get_user(user_id)
    assert updated_user["first_name"] == user_data["first_name"]
    assert updated_user["middle_name"] == update_user_data["middle_name"]
    assert updated_user["last_name"] == user_data["last_name"]

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_delete_users(db_connection):
    user_id = create_user(
        **{"first_name": "John", "middle_name": "E.", "last_name": "Doe"}
    )
    user_id = delete_user(user_id)
    assert user_id == user_id

    result = (
        db_connection.execute(select(users).where(users.c.id == user_id))
        .mappings()
        .all()
    )

    assert len(result) == 0


# bad cases


def test_bad_create_user(db_connection):
    user_id = create_user(first_name=None, middle_name=None, last_name=None)
    assert user_id is None
    result = (
        db_connection.execute(select(users).where(users.c.id == user_id))
        .mappings()
        .all()
    )
    assert len(result) == 0
