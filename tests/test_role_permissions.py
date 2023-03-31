from sqlalchemy import delete, select
from users_db.schema import Role, role_permission

from users_db.role_permissions import (
    create_permission_for_role,
    create_permissions_for_role,
    get_permissions_for_role,
    get_role_permission,
    update_permissions_for_role,
    delete_permission_for_role,
    delete_role_permissions,
)

from users_db.role_permissions import (
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN,
    ROLE_USER,
)


def test_create_permission_for_role(db_connection):
    permission = "read_test"
    permission_id = create_permission_for_role(ROLE_ADMIN, permission)
    rows = db_connection.execute(
        select(role_permission).where(role_permission.c.permission == permission)
    )
    row = rows.mappings().one()
    assert dict(row) == {
        "id": permission_id,
        "permission": permission,
        "role": Role.ADMIN,
    }

    db_connection.execute(
        delete(role_permission).where(role_permission.c.id == permission_id)
    )
    db_connection.commit()


def test_create_permissions_for_role(db_connection):
    permissions = ["read_test", "write_test"]
    permission_ids = create_permissions_for_role(ROLE_SUPER_ADMIN, permissions)
    rows = db_connection.execute(select(role_permission))
    rows = rows.mappings().all()
    assert [dict(row) for row in rows] == [
        {"id": id, "permission": permission, "role": Role.SUPER_ADMIN}
        for id, permission in zip(permission_ids, permissions)
    ]

    db_connection.execute(
        delete(role_permission).where(role_permission.c.id.in_(permission_ids))
    )
    db_connection.commit()


def test_get_permission(db_connection):
    permission = "read_test))))"
    permission_id = create_permission_for_role(ROLE_USER, permission)
    row = get_role_permission(permission_id)
    assert dict(row) == {
        "id": permission_id,
        "role": ROLE_USER,
        "permission": permission,
    }

    db_connection.execute(
        delete(role_permission).where(role_permission.c.id == permission_id)
    )
    db_connection.commit()


def test_get_permissions_for_role(db_connection):
    permissions = ["read_test", "write_test"]
    permission_ids = create_permissions_for_role(ROLE_USER, permissions)
    row = get_permissions_for_role(ROLE_USER)
    assert len(row) == 1

    assert row[0]["role"] == ROLE_USER
    assert len(row[0]["permissions"]) == len(permission_ids)

    assert [dict(row) for row in row[0]["permissions"]] == [
        {"id": id, "permission": permission}
        for id, permission in zip(permission_ids, permissions)
    ]

    db_connection.execute(
        delete(role_permission).where(role_permission.c.id.in_(permission_ids))
    )
    db_connection.commit()


def test_update_permissions_for_role(db_connection):
    permissions = ["read_test", "write_test"]
    permission_id = create_permission_for_role(ROLE_USER, permissions[0])
    update_permissions_for_role(permission_id, permission="read_test_2")
    row = get_role_permission(permission_id)
    assert row["permission"] == "read_test_2"

    db_connection.execute(
        delete(role_permission).where(role_permission.c.id == permission_id)
    )
    db_connection.commit()


def test_delete_permission_for_role():
    permission = "read_test"
    permission_id = create_permission_for_role(ROLE_USER, permission)
    delete_permission_for_role(permission_id)
    row = get_role_permission(permission_id)
    assert row is None


def test_delete_role_permissions():
    permissions = ["read_test", "write_test"]
    create_permissions_for_role(ROLE_USER, permissions)
    delete_role_permissions(ROLE_USER)
    rows = get_permissions_for_role(ROLE_USER)
    assert len(rows) == 0
