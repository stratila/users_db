import os


def get_postgres_uri():
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres123")
    DB_USER = os.environ.get("DB_USER", "users_db")
    DB_NAME = os.environ.get("DB_NAME", "users_db")

    host = DB_HOST
    password = DB_PASSWORD
    user = DB_USER
    db_name = DB_NAME
    port = 54321 if host == "localhost" else 5432

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
