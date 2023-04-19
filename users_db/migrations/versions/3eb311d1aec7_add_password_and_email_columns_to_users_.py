"""add password and email columns to users table

Revision ID: 3eb311d1aec7
Revises: f102a531f12e
Create Date: 2023-03-28 15:02:52.495139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3eb311d1aec7"
down_revision = "f102a531f12e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("email", sa.String(length=64), nullable=False))
    op.add_column("users", sa.Column("password", sa.String(length=256), nullable=False))
    op.create_unique_constraint(None, "users", ["email"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="unique")
    op.drop_column("users", "password")
    op.drop_column("users", "email")
    # ### end Alembic commands ###
