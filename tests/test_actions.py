import pytest
from sqlalchemy import Connection, insert, select, delete

from users_db.schema import actions_history, users
from users_db.role_permissions import ROLE_ADMIN


def test_create_action(db_connection: Connection):
    [[user_id]] = db_connection.execute(
        insert(users)
        .values(
            first_name="user",
            last_name="user",
            middle_name="user",
            email="user@user.com",
            password="123",
            role=ROLE_ADMIN,
        )
        .returning(users.c.id)
    )

    [[action_history_id]] = db_connection.execute(
        insert(actions_history)
        .values(
            performer_id=user_id,
            target_id=user_id,
            description="Self Action",
        )
        .returning(actions_history.c.id)
    )

    db_connection.commit()

    user = db_connection.execute(select(users).where(users.c.id == user_id)).one()
    assert user.id == user_id

    actions_history_record = db_connection.execute(
        select(actions_history).where(actions_history.c.id == action_history_id)
    ).one()
    assert actions_history_record.id == action_history_id

    db_connection.execute(delete(actions_history))
    db_connection.execute(delete(users))
    db_connection.commit()
