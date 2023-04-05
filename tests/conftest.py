import pytest

from sqlalchemy import create_engine
from users_db.config import get_postgres_uri

@pytest.fixture(scope="session")
def db_connection():
    engine = create_engine(get_postgres_uri())
    with engine.connect() as conn:
        yield conn