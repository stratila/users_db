import enum
import time
from sqlalchemy import (
    Table,
    Enum,
    Column,
    Integer,
    String,
    UniqueConstraint,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Role(enum.Enum):
    SUPER_ADMIN = 1
    ADMIN = 2
    USER = 3


role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("role", Enum(Role), nullable=False),
    Column("permission", String(100), nullable=False),
    UniqueConstraint("role", "permission", name="role_permission_uq"),
)

users = Table(
    "users",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(64), nullable=False),
    Column("middle_name", String(64), nullable=True),
    Column("last_name", String(64), nullable=False),
    Column("email", String(64), nullable=False, unique=True),
    Column("password", String(256), nullable=False),
    Column("role", Enum(Role), nullable=False),
)


actions_history = Table(
    "actions",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("performer_id", ForeignKey("users.id"), nullable=False),
    Column("target_id", ForeignKey("users.id"), nullable=False),
    Column("description", String(64), nullable=True),
    Column("timestamp", Float, default=time.time, nullable=False),
)
