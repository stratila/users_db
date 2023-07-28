from sqlalchemy import insert, select, update, delete

from users_db.db import db_execute, db_transaction
from users_db.pagination import paginate
from users_db.schema import users


@db_transaction
def create_user(
    first_name, middle_name, last_name, email, password, role, db_conn=None
):
    return db_execute(
        insert(users).values(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role,
        ),
        db_conn=db_conn,
    )


@db_transaction
def get_user(user_id, db_conn=None):
    return db_execute(select(users).where(users.c.id == user_id), db_conn=db_conn)


@db_transaction
def get_hashed_password_by_email(email, db_conn=None):
    stmt = select(
        users.c.id, users.c.email, users.c.password.label("hashed_password")
    ).where(users.c.email == email)
    return db_execute(stmt, db_conn=db_conn)


@db_transaction
@paginate
def get_users(
    user_id=None,
    user_ids=None,
    first_name=None,
    middle_name=None,
    last_name=None,
    email=None,
    role=None,
    db_conn=None,
    is_paginated=False,
    page=None,
    page_size=None,
):
    stmt = select(users)

    if user_id:
        stmt = stmt.where(users.c.id == user_id)
    if user_ids:
        stmt = stmt.where(users.c.id.in_(user_ids))
    if first_name:
        stmt = stmt.where(users.c.first_name == first_name)
    if middle_name:
        stmt = stmt.where(users.c.middle_name == middle_name)
    if last_name:
        stmt = stmt.where(users.c.last_name == last_name)
    if email:
        stmt = stmt.where(users.c.email == email)
    if role:
        stmt = stmt.where(users.c.role == role)
    return stmt


@db_transaction
def update_user(
    user_id,
    db_conn=None,
    **values,
):
    stmt = update(users).where(users.c.id == user_id).values(**values)
    return db_execute(stmt, db_conn=db_conn)


@db_transaction
def delete_user(
    user_id,
    db_conn=None,
):
    stmt = delete(users).where(users.c.id == user_id)
    return db_execute(stmt, db_conn=db_conn)


@db_transaction
def bulk_delete_users(
    user_ids,
    db_conn=None,
):
    stmt = delete(users).where(users.c.id.in_(user_ids))
    return db_execute(stmt, db_conn=db_conn)
