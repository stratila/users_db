from typing import List
from sqlalchemy import insert, select, update, delete

# func.json_build_array, func.json_build_object, func.json_agg
from sqlalchemy.sql.expression import func

from users_db.db import db_transaction, db_execute
from users_db.schema import Role, role_permission

ROLE_SUPER_ADMIN = Role.SUPER_ADMIN.name
ROLE_ADMIN = Role.ADMIN.name
ROLE_USER = Role.USER.name


@db_transaction
def create_permission_for_role(role: str, permission: str, db_conn=None):
    stmt = insert(role_permission).values(role=role, permission=permission)
    return db_execute(stmt, db_conn=db_conn)


@db_transaction
def create_permissions_for_role(role: str, permissions: List[str], db_conn=None):
    stmt = insert(role_permission).values(
        [{"role": role, "permission": permission} for permission in permissions]
    )
    return db_execute(stmt, db_conn=db_conn)


@db_transaction
def get_role_permission(role_permission_id, db_conn=None):
    select_stmt = select(role_permission).where(
        role_permission.c.id == role_permission_id
    )
    row = db_execute(select_stmt, db_conn=db_conn)
    return row


@db_transaction
def get_permissions_for_role(role: str, db_conn=None):
    select_stmt = (
        select(
            role_permission.c.role,
            func.json_agg(
                func.json_build_object(
                    "id",
                    role_permission.c.id,
                    "permission",
                    role_permission.c.permission,
                )
            ).label("permissions"),
        )
        .where(role_permission.c.role == role)
        .group_by(role_permission.c.role)
    )
    row = db_execute(select_stmt, db_conn=db_conn)
    return row


@db_transaction
def update_permissions_for_role(role_permission_id, db_conn=None, **values):
    update_stmt = (
        update(role_permission)
        .where(role_permission.c.id == role_permission_id)
        .values(**values)
    )
    return db_execute(update_stmt, db_conn=db_conn)


@db_transaction
def delete_permission_for_role(role_permission_id, db_conn=None):
    delete_stmt = delete(role_permission).where(
        role_permission.c.id == role_permission_id
    )
    return db_execute(delete_stmt, db_conn=db_conn)


@db_transaction
def delete_role_permissions(role, db_conn=None):
    delete_stmt = delete(role_permission).where(role_permission.c.role == role)
    return db_execute(delete_stmt, db_conn=db_conn)
