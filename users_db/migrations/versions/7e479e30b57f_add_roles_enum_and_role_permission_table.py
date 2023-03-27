"""add roles enum and role_permission table

Revision ID: 7e479e30b57f
Revises: f46112e923d8
Create Date: 2023-03-27 21:55:46.495304

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "7e479e30b57f"
down_revision = "f46112e923d8"
branch_labels = None
depends_on = None

name = "role_enum"
options = ("ADMIN", "USER")

new_type = sa.Enum(*options, name=name)

# see values of enum:
# SELECT unnest(enum_range(NULL::role_enum)) AS role_enum;

# Future enum updates:
# https://stackoverflow.com/a/45615354/6534115
# https://stackoverflow.com/a/14845740/6534115
# https://stackoverflow.com/a/33617845/6534115


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("role", new_type, nullable=False),
        sa.Column("permission", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "users",
        sa.Column("role", new_type, nullable=True),
    )

    op.execute("UPDATE users SET role = 'USER'")
    op.alter_column("users", "role", nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "role")
    op.drop_table("role_permissions")
    # ### end Alembic commands ###
    new_type.drop(op.get_bind(), checkfirst=True)
