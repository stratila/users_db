import pytest
import sqlalchemy
from sqlalchemy import create_engine, select, delete
from users_db.config import get_postgres_uri
from users_db.schema import users
from users_db.users import (
    create_user,
    get_user,
    get_hashed_password_by_email,
    get_users,
    update_user,
    delete_user,
    bulk_delete_users,
)


def test_create_user(db_connection):
    first_name = "John"
    middle_name = None
    last_name = "Doe"
    email = "email@email.com"
    password = "password"
    role = "USER"

    user_id = create_user(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        email=email,
        password=password,
        role=role,
    )

    result = (
        db_connection.execute(select(users).where(users.c.id == user_id))
        .mappings()
        .one()
    )
    result = dict(result)
    assert result["id"] == user_id
    assert result["first_name"] == first_name
    assert result["last_name"] == last_name
    assert result["middle_name"] == middle_name
    assert result["email"] == email
    assert result["password"] == password
    assert result["role"].name == role

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_get_user(db_connection):
    user_data = {
        "first_name": "John",
        "middle_name": "E.",
        "last_name": "Doe",
        "email": "email@email.com",
        "password": "password",
        "role": "USER",
    }

    user_id = create_user(**user_data)
    user = get_user(user_id)

    assert user["id"] == user_id
    for key in user_data.keys():
        if key == "password":
            # password should not be returned
            user.get(key) is None
            continue
        assert user[key] == user_data[key]

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_get_hashed_password_by_email(db_connection):
    user_data = {
        "first_name": "John",
        "middle_name": "E.",
        "last_name": "Doe",
        "email": "email@email.com",
        "role": "USER",
        "password": "hashed",
    }

    user_id = create_user(**user_data)
    data = get_hashed_password_by_email(user_data["email"])

    assert data["id"] == user_id
    assert data["email"] == user_data["email"]
    assert data["hashed_password"] == user_data["password"]

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_get_users(db_connection):
    users_data = [
        {
            "first_name": "John",
            "middle_name": "E.",
            "last_name": "Doe",
            "role": "USER",
            "email": "email1@email.com",
            "password": "password",
        },
        {
            "first_name": "Madeline",
            "middle_name": "J.",
            "last_name": "Doe",
            "role": "USER",
            "email": "email2@email.com",
            "password": "password",
        },
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
                    if key == "password":
                        # password should not be returned
                        user.get(key) is None
                        continue
                    assert user[key] == user_data[key]

    # clean up
    for user_id in user_ids:
        db_connection.execute(delete(users).where(users.c.id == user_id))
        db_connection.commit()


def test_update_users(db_connection):
    user_data = {
        "first_name": "John",
        "middle_name": "E.",
        "last_name": "Doe",
        "role": "USER",
        "email": "email@email.com",
        "password": "password",
    }
    update_user_data = {"middle_name": "Emmanuel"}
    user_id = create_user(**user_data)
    updated_user = update_user(user_id, **update_user_data)
    assert updated_user["id"] == user_id
    assert updated_user["first_name"] == user_data["first_name"]
    assert updated_user["middle_name"] == update_user_data["middle_name"]
    assert updated_user["last_name"] == user_data["last_name"]
    assert updated_user["role"] == user_data["role"]
    assert updated_user["email"] == user_data["email"]

    # clean up
    db_connection.execute(delete(users).where(users.c.id == user_id))
    db_connection.commit()


def test_delete_users(db_connection):
    user_id = create_user(
        **{
            "first_name": "John",
            "middle_name": "E.",
            "last_name": "Doe",
            "role": "USER",
            "email": "email@email@.com",
            "password": "password",
        }
    )
    user_id = delete_user(user_id)
    assert user_id == user_id

    result = (
        db_connection.execute(select(users).where(users.c.id == user_id))
        .mappings()
        .all()
    )

    assert len(result) == 0


def test_bulk_delete_users(db_connection):
    user_ids = []
    for i in range(10):
        user_ids.append(
            create_user(
                **{
                    "first_name": "John",
                    "middle_name": "E.",
                    "last_name": "Doe",
                    "role": "USER",
                    "email": f"email{i}@email.com",
                    "password": "password",
                }
            )
        )
    deleted_count = bulk_delete_users(user_ids)
    assert deleted_count == len(user_ids)
    result = (
        db_connection.execute(select(users).where(users.c.id.in_(user_ids)))
        .mappings()
        .all()
    )
    assert len(result) == 0

    # clean up
    db_connection.execute(delete(users).where(users.c.id.in_(user_ids)))
    db_connection.commit()


# bad cases


def test_bad_create_user(db_connection):
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        user_id = create_user(
            first_name=None,
            middle_name=None,
            last_name=None,
            email=None,
            password=None,
            role=None,
        )