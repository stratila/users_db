### How to run alembic migrations

1. We wrap alembic commands into functions in `migrations/__init__.py`. This functions are imported by the `commands.py` file in the users_db module. 

2. This `commands.py` file wraps the functions defined in the `alembic/__init__.py` file, providing command   line interface to this functions using Click library. Also, these commands always knows where the working directory with `alembic.ini` file is. We install this commands as Poetry scripts, so we can run them from the command line and don't worry about `alembic.ini` file location.

3. If `commands.py` doesn't have the command you need, you'll have to add it in `migrations/__init__.py`, then define click command in `commands.py` and finally install it as a Poetry script

4. In oder to create the migration, first you need to start containers `docker compose up -d`, make changes in the schema.py by defining the new models or changing the existing ones, and then run `docker compose exec db alembic_revision --autogenerate=True -m "migration message"`.

5. After that, you need to run `docker compose exec db alembic_upgrade --revision head` to apply the migration to the database.


Enum migration example:
```python
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3c52d30040ed"
down_revision = "27133ce191df"
branch_labels = None
depends_on = None

TYPE_NAME = "role_enum"
OLD_VALUES = ["SUPER_ADMIN", "ADMIN", "USER"]
NEW_VALUES = [*OLD_VALUES, "EMPLOYEE"]

# key: table name, value: column name
TABLES_TO_UPDATE = {
    "users": "role",
    "role_permissions": "role",
}


def change_enum_and_alter_tables(
    enum_name,
    enum_values,
    table_column_dict,
):
    conn = op.get_bind()

    new_type = sa.Enum(*enum_values, name=enum_name)

    # we rename to tmp_ to create a new type with the same name and new values
    op.execute(f"ALTER TYPE {enum_name} RENAME TO tmp_{enum_name}")

    new_type.create(conn)

    for table, column in table_column_dict.items():
        op.alter_column(
            table_name=table,
            column_name=column,
            type_=new_type,
            postgresql_using=f"{column}::text::{enum_name}",
        )

    op.execute(f"DROP TYPE tmp_{enum_name}")


def upgrade() -> None:
    change_enum_and_alter_tables(
        enum_name=TYPE_NAME,
        enum_values=NEW_VALUES,
        table_column_dict=TABLES_TO_UPDATE,
    )


def downgrade() -> None:
    change_enum_and_alter_tables(
        enum_name=TYPE_NAME,
        enum_values=OLD_VALUES,
        table_column_dict=TABLES_TO_UPDATE,
    )
```