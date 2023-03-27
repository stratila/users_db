"""empty message

Revision ID: f102a531f12e
Revises: 7e479e30b57f
Create Date: 2023-03-27 22:47:41.244980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f102a531f12e"
down_revision = "7e479e30b57f"
branch_labels = None
depends_on = None

name = "role_enum"
tmp_name = "tmp_" + name

old_options = ("ADMIN", "USER")
new_options = sorted(old_options + ("SUPER_ADMIN",))

new_type = sa.Enum(*new_options, name=name)
old_type = sa.Enum(*old_options, name=name)


def upgrade() -> None:
    op.execute("ALTER TYPE role_enum RENAME TO " + tmp_name)
    new_type.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "users", "role", type_=new_type, postgresql_using=f"role::text::{name}"
    )
    op.alter_column(
        "role_permissions",
        "role",
        type_=new_type,
        postgresql_using=f"role::text::{name}",
    )
    op.execute("DROP TYPE " + tmp_name)


def downgrade() -> None:
    op.execute("ALTER TYPE role_enum RENAME TO " + tmp_name)
    old_type.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "users", "role", type_=old_type, postgresql_using=f"role::text::{name}"
    )
    op.alter_column(
        "role_permissions",
        "role",
        type_=old_type,
        postgresql_using=f"role::text::{name}",
    )
    op.execute("DROP TYPE " + tmp_name)
