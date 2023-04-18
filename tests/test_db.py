from users_db.db import (
    base_transaction,
    db_transaction,
    thread_local,
)

# TODO
# delete base class and use only db_transaction
# derrive fake_transaction from db_transaction
# add print statements to open_connection, close_connection, commit, rollback
# test failed case when function raises exception, check rollback and stack is cleared


class fake_transaction(base_transaction):
    def __init__(self, func):
        super().__init__(func)
        self.func = func
        self.connection = None

    def open_connection(self):
        if hasattr(thread_local, "transaction_stack"):
            transaction = (
                thread_local.transaction_stack[-1]
                if thread_local.transaction_stack
                else None
            )
            if transaction:
                self.connection = transaction.connection

        if self.connection is None:
            print("Opening connection...")
            self.connection = "conn"

    def close_connection(self):
        print("Closing connection...")
        pass

    def commit(self):
        pass

    def rollback(self):
        pass


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
        "func3 called\nClosing connection...\n"
    )
    captured = capsys.readouterr()
    assert captured.out == expected_output, "Test failed"

    # Check that the transaction stack was cleared
    assert not thread_local.transaction_stack, "Test failed"


