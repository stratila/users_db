import logging
from typing import Union
from enum import Enum

from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.sql.dml import Insert, Update, Delete
from sqlalchemy.exc import SQLAlchemyError

from users_db import config

log = logging.getLogger(__name__)

engine = create_engine(url=config.get_postgres_uri())


REMOVE_KEYS = ["password"]


def secure_result(result: Union[dict, list]):
    """
    secure_result removes sensitive rows from the result
    """
    if isinstance(result, dict):
        for key in REMOVE_KEYS:
            if key in result:
                del result[key]
    elif isinstance(result, list):
        for item in result:
            secure_result(item)

    return result


def serialize_enums(result: Union[dict, list]):
    """
    serialize_enums converts enums to strings
    """
    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, Enum):
                result[key] = value.name
    elif isinstance(result, list):
        for item in result:
            serialize_enums(item)

    return result


def db_connection(f):
    """
    db_connection decorator supports executing select, insert, update, delete
    operations with a single transaction; post-process data in a user friendly manner
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        with engine.connect() as connection:
            try:
                r = f(*args, **kwargs, db_conn=connection)

                if isinstance(r, (dict, list)):
                    # post-process data here, for example excluding sensitive rows
                    result = r
                elif isinstance(r, (Insert, Update)):
                    result = connection.execute(r.returning(r.table.c.id)).all()
                    result = result[0][0] if len(result) == 1 else [r[0] for r in result]
                    connection.commit()
                elif isinstance(r, Delete):
                    result = connection.execute(r)
                    result = result.rowcount
                    connection.commit()

                result = secure_result(serialize_enums(result))
                return result
            except SQLAlchemyError as err:
                log.error(f"Error: {err}")
                connection.rollback()

    return wrapped
