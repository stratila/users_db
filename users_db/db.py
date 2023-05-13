import abc
import logging
import threading

from typing import Union
from enum import Enum

from sqlalchemy import Connection, create_engine
from sqlalchemy.sql.dml import Insert, Update, Delete
from sqlalchemy.sql.selectable import Select
from sqlalchemy.exc import SQLAlchemyError

from users_db import config
from users_db.errors import DatabaseError, SqlAlchemyDatabaseError

log = logging.getLogger(__name__)

engine = create_engine(url=config.get_postgres_uri())

thread_local = threading.local()

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


def dict_or_list(result):
    """Returns a dictionary or a list of dictionaries"""
    return (
        dict(result[0]._mapping)
        if len(result) == 1
        else [dict(r._mapping) for r in result]
    )


def id_or_ids_list(result):
    return result[0][0] if len(result) == 1 else [r[0] for r in result]


class base_transaction(abc.ABC):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            if not hasattr(thread_local, "transaction_stack"):
                thread_local.transaction_stack = []

            self.connection = self.get_connection()
            if not self.connection:
                self.open_connection()

            thread_local.transaction_stack.append(self)
            # execute a function and return a result
            return self.func(*args, **kwargs, db_conn=self.connection)

        except DatabaseError as err:
            # rollback a transaction if an exception occurred and clear the stack by
            # setting it to an empty list

            if thread_local.transaction_stack:
                self.rollback()
                self.close_connection()
                thread_local.transaction_stack = []
            raise err
        finally:
            if thread_local.transaction_stack:
                if thread_local.transaction_stack[0] == self:
                    self.commit()
                    self.close_connection()
                thread_local.transaction_stack.pop()

    @abc.abstractmethod
    def get_connection(self):
        pass

    @abc.abstractmethod
    def open_connection(self):
        pass

    @abc.abstractmethod
    def close_connection(self):
        pass

    @abc.abstractmethod
    def rollback(self):
        pass

    @abc.abstractmethod
    def commit(self):
        pass


class db_transaction(base_transaction):
    def __init__(self, func):
        super().__init__(func)
        self.connection = None

    def get_connection(self):
        transaction = (
            thread_local.transaction_stack[-1]
            if thread_local.transaction_stack
            else None
        )
        return transaction.connection if transaction else None

    def open_connection(self):
        try:
            # checks whether there is a transaction in the stack
            transaction = (
                thread_local.transaction_stack[-1]
                if thread_local.transaction_stack
                else None
            )
            if transaction:
                self.connection = transaction.connection

            if self.connection is None:
                self.connection = engine.connect()
        except SQLAlchemyError as err:
            raise SqlAlchemyDatabaseError(err)

    def close_connection(self):
        if self.connection and not self.connection.closed:
            self.connection.close()

    def rollback(self):
        if self.connection and not self.connection.closed:
            self.connection.rollback()

    def commit(self):
        if self.connection:
            self.connection.commit()


def db_execute(statement, db_conn: Connection):
    """
    db_connection function supports executing select, insert, update, delete
    queries and post-process result data in a user friendly manner
    """
    try:
        if isinstance(statement, Select):
            # post-process data here, for example excluding sensitive rows
            result = db_conn.execute(statement).all()
            result = dict_or_list(result) or None

        elif isinstance(statement, Insert):
            # return the id of the inserted row or a list of ids
            result = db_conn.execute(statement.returning(statement.table.c.id)).all()
            result = id_or_ids_list(result)

        elif isinstance(statement, Update):
            # update returns the whole object or a list of objects
            result = db_conn.execute(statement.returning(statement.table)).all()
            result = dict_or_list(result)

        elif isinstance(statement, Delete):
            # return the number of deleted rows
            result = db_conn.execute(statement)
            result = result.rowcount

        # post-process data here, for example excluding sensitive rows
        result = secure_result(serialize_enums(result))
        return result
    except SQLAlchemyError as err:
        # wrap SQLAlchemyError into a custom exception (DatabaseError) to handle it
        # later base_transaction
        raise SqlAlchemyDatabaseError(err)
