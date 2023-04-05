### How to run alembic migrations

1. We wrap alembic commands into functions in `migrations/__init__.py`. This functions are imported by the `commands.py` file in the users_db module. 

2. This `commands.py` file wraps the functions defined in the `alembic/__init__.py` file, providing command   line interface to this functions using Click library. Also, these commands always knows where the working directory with `alembic.ini` file is. We install this commands as Poetry scripts, so we can run them from the command line and don't worry about `alembic.ini` file location.

3. If `commands.py` doesn't have the command you need, you'll have to add it in `migrations/__init__.py`, then define click command in `commands.py` and finally install it as a Poetry script

4. In oder to create the migration, first you need to start containers `docker compose up -d`, make changes in the schema.py by defining the new models or changing the existing ones, and then run `docker compose exec db alembic_revision --autogenerate=True -m "migration message"`.

5. After that, you need to run `docker compose exec db alembic_upgrade --revision head` to apply the migration to the database.


TODO add the example of the migration for Enum, because alembic doesn't support the autogeneration for Enum