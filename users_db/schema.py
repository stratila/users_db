from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

users = Table(
    "users",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(16), nullable=False),
    Column("middle_name", String(16), nullable=True),
    Column("last_name", String(16), nullable=False),
)
