import logging

from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.sql.dml import Insert, Update, Delete
from sqlalchemy.exc import SQLAlchemyError

from users_db import config

log = logging.getLogger(__name__)

engine = create_engine(url=config.get_postgres_uri())


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
                    result = connection.execute(r.returning(r.table.c.id))
                    result = result.one()[0]
                    connection.commit()
                elif isinstance(r, Delete):
                    result = connection.execute(r)
                    result = result.rowcount
                    connection.commit()

                return result
            except SQLAlchemyError as err:
                log.error(f"Error: {err}")
                connection.rollback()

    return wrapped
