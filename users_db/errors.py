import sqlalchemy.exc


class DatabaseError(Exception):
    pass


class SqlAlchemyDatabaseError(DatabaseError):
    """A class that wraps SqlAlchemy errors and dis
    them to the user in a more user-friendly way."""

    integrity_error_msg = "An integrity error occurred while accessing the database: {}"
    data_error_msg = "A data error occurred while accessing the database: {}"
    operational_error_msg = "A database error occurred while accessing the database: {}"
    programming_error_msg = (
        "A programming error occurred while accessing the database: {}"
    )
    interface_error_msg = "An interface error occurred while accessing the database: {}"
    timeout_error_msg = "A timeout error occurred while accessing the database: {}"

    error_messages = {
        sqlalchemy.exc.IntegrityError: integrity_error_msg,
        sqlalchemy.exc.DataError: data_error_msg,
        sqlalchemy.exc.OperationalError: operational_error_msg,
        sqlalchemy.exc.ProgrammingError: programming_error_msg,
        sqlalchemy.exc.InterfaceError: interface_error_msg,
        sqlalchemy.exc.TimeoutError: timeout_error_msg,
    }

    def __init__(self, original_exception):
        self.original_exception = original_exception
        error_type = type(original_exception)
        error_message = self.error_messages.get(
            error_type, "An error occurred while accessing the database: {}"
        )
        message = error_message.format(str(original_exception))
        super().__init__(message)


class UserDatabaseError(DatabaseError):
    """A class that wraps user database errors"""

    def __init__(self, message):
        super().__init__(message)
