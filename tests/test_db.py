import pytest
from users_db.db import base_transaction, thread_local
from users_db.errors import DatabaseError, UserDatabaseError


# TODO
# add print statements to open_connection, close_connection, commit, rollback
# test failed case when function raises exception, check rollback and stack is cleared


class fake_transaction(base_transaction):
    def __init__(self, func):
        super().__init__(func)
        self.func = func
        self.connection = None

    def get_connection(self):
        transaction = (
            thread_local.transaction_stack[-1]
            if thread_local.transaction_stack
            else None
        )
        return transaction.connection if transaction else None

    def open_connection(self):
        if self.connection is None:
            print("Opening connection...")
            self.connection = "opened"

    def close_connection(self):
        if self.connection and self.connection != "closed":
            self.connection = "closed"
            print("Closing connection...")

    def commit(self):
        if self.connection and self.connection != "closed":
            print("Committing...")

    def rollback(self):
        if self.connection and self.connection != "closed":
            print("Rolling back...")


def test_transaction_decorator(capsys):
    @fake_transaction
    def func1(db_conn=None):
        print("func1 called")
        func2()

    @fake_transaction
    def func2(db_conn=None):
        print("func2 called")
        func3()

    @fake_transaction
    def func3(db_conn=None):
        print("func3 called")

    # Call the function and check the output
    func1()
    expected_output = (
        "Opening connection...\nfunc1 called\nfunc2 called\n"
        "func3 called\nCommitting...\nClosing connection...\n"
    )
    captured = capsys.readouterr()
    assert captured.out == expected_output, "Test failed"

    # Check that the transaction stack was cleared
    assert not thread_local.transaction_stack, "Test failed"


def test_transaction_decorator_failed(capsys):
    @fake_transaction
    def func1(db_conn=None):
        print("func1 called")
        func2()

    @fake_transaction
    def func2(db_conn=None):
        print("func2 called")
        func3()

    @fake_transaction
    def func3(db_conn=None):
        print("func3 called")
        raise UserDatabaseError("Test exception")

    # Call the function and check the output
    with pytest.raises(DatabaseError):
        func1()

    expected_output = (
        "Opening connection...\nfunc1 called\nfunc2 called\n"
        "func3 called\nRolling back...\nClosing connection...\n"
    )
    captured = capsys.readouterr()
    assert captured.out == expected_output, "Test failed"

    # Check that the transaction stack was cleared
    assert not thread_local.transaction_stack, "Test failed"
