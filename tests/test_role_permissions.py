import pytest
import csv
from io import StringIO

from sqlalchemy import delete, select

from users_db.db import serialize_enums, dict_or_list
from users_db.schema import Role, role_permission


from users_db.role_permissions import (
    create_permission_for_role,
    create_permissions_for_role,
    get_permissions_for_role,
    get_role_permission,
    get_role_permissions,
    delete_role_permissions,
    update_permissions_for_role,
    update_role_permission_table_with_csv,
)

from users_db.role_permissions import (
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN,
    ROLE_USER,
)


# dataset fixture for role_permission table
@pytest.fixture(scope="function")
def role_permission_dataset(db_connection):
    data = [
        {"role": Role.SUPER_ADMIN.name, "permission": "read_test"},
        {"role": Role.SUPER_ADMIN.name, "permission": "write_test"},
        {"role": Role.ADMIN.name, "permission": "read_test"},
        {"role": Role.ADMIN.name, "permission": "write_test"},
        {"role": Role.USER.name, "permission": "read_test"},
        {"role": Role.USER.name, "permission": "write_test"},
    ]

    for row in data:
        permission_id = create_permission_for_role(row["role"], row["permission"])
        row["role"] = row["role"]
        row.update({"id": permission_id})

    yield data

    for row in data:
        db_connection.execute(
            delete(role_permission).where(role_permission.c.id == row["id"])
        )
    db_connection.commit()


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


def test_get_role_permissions(db_connection, role_permission_dataset):
    # Checks all of the rows in the dataset are returned
    rows = get_role_permissions()
    rows = rows or []
    assert len(rows) == len(role_permission_dataset)

    assert rows == [
        {"id": row["id"], "role": row["role"], "permission": row["permission"]}
        for row in role_permission_dataset
    ]

    # Checks permissions by ids
    rows = get_role_permissions(
        role_permission_ids=[row["id"] for row in role_permission_dataset]
    )
    rows = rows or []
    assert len(rows) == len(role_permission_dataset)

    assert rows == [
        {"id": row["id"], "role": row["role"], "permission": row["permission"]}
        for row in role_permission_dataset
    ]

    # Checks permissions by role
    rows = get_role_permissions(role=Role.SUPER_ADMIN)
    rows = rows or []
    assert len(rows) == 2
    assert rows == [
        {"id": row["id"], "role": row["role"], "permission": row["permission"]}
        for row in role_permission_dataset
        if row["role"] == Role.SUPER_ADMIN.name
    ]

    # Checks permissions by permission
    rows = get_role_permissions(permission="read_test")
    rows = rows or []
    assert len(rows) == 3
    assert rows == [
        {"id": row["id"], "role": row["role"], "permission": row["permission"]}
        for row in role_permission_dataset
        if row["permission"] == "read_test"
    ]


def test_get_permissions_for_role(db_connection):
    permissions = ["read_test", "write_test"]
    permission_ids = create_permissions_for_role(ROLE_USER, permissions)
    row = get_permissions_for_role(ROLE_USER)

    assert row["role"] == ROLE_USER
    assert len(row["permissions"]) == len(permission_ids)

    assert [dict(row) for row in row["permissions"]] == [
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
    updated_record = update_permissions_for_role(
        permission_id, permission="read_test_2"
    )
    assert updated_record["id"] == permission_id

    row = get_role_permission(permission_id)
    assert row["permission"] == "read_test_2"

    db_connection.execute(
        delete(role_permission).where(role_permission.c.id == permission_id)
    )
    db_connection.commit()


def test_delete_role_permission(db_connection, role_permission_dataset):
    rows = get_role_permissions()
    assert len(rows) == len(role_permission_dataset)
    delete_role_permissions()
    rows = db_connection.execute(
        select(role_permission)
    )
    assert rows.rowcount == 0


def test_update_role_permission_table_with_csv(role_permission_dataset, db_connection):
    # StringIO is used to create a file-like object
    # that contains the contents of the CSV file.

    csv_file = StringIO(
        """role,permission
SUPER_ADMIN,read_test
SUPER_ADMIN,write_test
ADMIN,read_test
ADMIN,write_test
SUPER_ADMIN,read_test_new
SUPER_ADMIN,write_test_new
"""
    )
    # will be deleted form the dataset
    # USER,read_test
    # USER,write_test

    # new
    # SUPER_ADMIN,read_test_new
    # SUPER_ADMIN,write_test_new
    new_role_permissions = {
        (Role.SUPER_ADMIN.name, "read_test_new"),
        (Role.SUPER_ADMIN.name, "write_test_new"),
    }

    # get all records ids except USER
    role_permissions_old = get_role_permissions()
    role_permissions_old_ids = [
        row["id"] for row in role_permissions_old if row["role"] != Role.USER.name
    ]

    # open and read csv
    csv_list = csv.DictReader(csv_file, delimiter=",")
    csv_list = [{k: v for k, v in row.items()} for row in csv_list]

    # update table
    update_role_permission_table_with_csv(csv_list)

    # check records that simultaneously exist in the old and new datasets persist
    rows = db_connection.execute(
        select(role_permission).where(
            role_permission.c.id.in_(role_permissions_old_ids)
        )
    )

    rows = serialize_enums(dict_or_list(rows.all()))
    assert len(rows) == len(role_permissions_old_ids)

    # check new records
    rows = db_connection.execute(
        select(role_permission)
        .where(role_permission.c.role == Role.SUPER_ADMIN.name)
        .where(role_permission.c.permission.in_([rp[1] for rp in new_role_permissions]))
    )
    rows = serialize_enums(dict_or_list(rows.all()))

    assert len(rows) == len(new_role_permissions)
    assert {(row["role"], row["permission"]) for row in rows} == new_role_permissions

    # check deleted records
    rows = db_connection.execute(
        select(role_permission).where(role_permission.c.role == Role.USER.name)
    )
    rows = serialize_enums(dict_or_list(rows.all()))
    assert len(rows) == 0

    # clean up
    db_connection.execute(
        delete(role_permission).where(
            role_permission.c.permission.in_([rp[1] for rp in new_role_permissions])
        )
    )
    db_connection.commit()
