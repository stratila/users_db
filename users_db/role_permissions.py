import logging
from typing import List
from sqlalchemy import insert, select, update, delete

# func.json_build_array, func.json_build_object, func.json_agg
from sqlalchemy.sql.expression import func

from users_db.db import db_transaction, db_execute
from users_db.schema import Role, role_permission

ROLE_SUPER_ADMIN = Role.SUPER_ADMIN.name
ROLE_ADMIN = Role.ADMIN.name
ROLE_USER = Role.USER.name


log = logging.getLogger(__name__)


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
def get_role_permissions(
    role_permission_ids=None, role=None, permission=None, db_conn=None
):
    select_stmt = select(role_permission)

    if role_permission_ids:
        select_stmt = select_stmt.where(role_permission.c.id.in_(role_permission_ids))
    if role:
        select_stmt = select_stmt.where(role_permission.c.role == role)
    if permission:
        select_stmt = select_stmt.where(role_permission.c.permission == permission)
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
def delete_role_permissions(
    id=None, ids=None, role=None, permission=None, db_conn=None
):
    delete_stmt = delete(role_permission)

    if id:
        delete_stmt = delete_stmt.where(role_permission.c.id == id)
    if ids:
        delete_stmt = delete_stmt.where(role_permission.c.id.in_(ids))
    if role:
        delete_stmt = delete_stmt.where(role_permission.c.role == role)
    if permission:
        delete_stmt = delete_stmt.where(role_permission.c.permission == permission)

    return db_execute(delete_stmt, db_conn=db_conn)


@db_transaction
def update_role_permission_table_with_csv(
    role_permission_list_csv: list[dict], logged: bool = False, db_conn=None
):
    """
    Check if the role_permission_list_csv is different from the role_permission
    table,deletes the role_permission that are not in the role_permission_list_csv
    and creates the role_permission that are in the role_permission_list_csv but
    not in the role_permission table. Does not touches the role_permission that are
    in both the role_permission_list_csv and the role_permission table.
    """
    role_permission_db_list = get_role_permissions() or []

    actual_role_permission_set = {
        (rpc["role"], rpc["permission"]) for rpc in role_permission_list_csv
    }
    existing_role_permission_set = {
        (rpd["role"], rpd["permission"]) for rpd in role_permission_db_list
    }

    to_create_role_permissions = list(
        (actual_role_permission_set - existing_role_permission_set)
    )
    to_delete_role_permissions = list(
        (existing_role_permission_set - actual_role_permission_set)
    )
    unchanged_role_permissions = list(
        existing_role_permission_set & actual_role_permission_set
    )

    to_delete_ids = [
        rp["id"]
        for rp in role_permission_db_list
        if (rp["role"], rp["permission"]) in to_delete_role_permissions
    ]

    if to_delete_ids:
        delete_role_permissions(ids=to_delete_ids)
    if to_create_role_permissions:
        for role, permission in to_create_role_permissions:
            create_permission_for_role(role, permission)

    return {
        "to_create_role_permissions": to_create_role_permissions,
        "to_delete_role_permissions": to_delete_role_permissions,
        "unchanged_role_permissions": unchanged_role_permissions,
    }
