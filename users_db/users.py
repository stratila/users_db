from sqlalchemy import insert, select, update, delete

from users_db.db import db_connection
from users_db.schema import users


@db_connection
def create_user(first_name, middle_name, last_name, db_conn):
    return insert(users).values(
        first_name=first_name, middle_name=middle_name, last_name=last_name
    )


@db_connection
def get_user(user_id, db_conn=None):
    stmt = select(users).where(users.c.id == user_id)
    rows = db_conn.execute(stmt)
    rows = rows.mappings().one()
    return dict(rows)


@db_connection
def get_users(
    user_id=None,
    user_ids=None,
    first_name=None,
    middle_name=None,
    last_name=None,
    db_conn=None,
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

    rows = db_conn.execute(stmt)
    rows = [dict(row) for row in rows.mappings().all()]
    return rows


@db_connection
def update_user(
    user_id,
    db_conn=None,
    **values,
):
    return update(users).where(users.c.id == user_id).values(**values)


@db_connection
def delete_user(
    user_id,
    db_conn=None,
):
    return delete(users).where(users.c.id == user_id)


@db_connection
def bulk_delete_users(
    user_ids,
    db_conn=None,
):
    return delete(users).where(users.c.id.in_(user_ids))
