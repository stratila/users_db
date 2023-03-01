import os


def get_postgres_uri():
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres123")

    host = DB_HOST
    password = DB_PASSWORD
    port = 54321 if host == "localhost" else 5432
    user, db_name = "users_db", "users_db"

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
