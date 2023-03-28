#!/bin/bash

TESTDB=testdb

# 1) dump app's database schema to /var/tmp
#     (in order not to run migrations on every test execution
#      idea seen in: https://dba.stackexchange.com/a/10475)
# 2) drop test database if exists
# 3) create test database
# 3) restore database schema to test database

docker compose exec --no-TTY -e TESTDB=$TESTDB postgres sh -c '
    pg_dump --format=c --schema-only $POSTGRES_DB --username=$POSTGRES_USER > /var/tmp/schema.sql;
    dropdb $TESTDB --if-exists --username=$POSTGRES_USER;
    createdb $TESTDB --username=$POSTGRES_USER;
    pg_restore --format=c --schema-only --dbname=$TESTDB --username=$POSTGRES_USER /var/tmp/schema.sql;
'

# run tests
docker compose exec --no-TTY -e DB_NAME=testdb db sh -c 'pytest tests --cov=/users_db --cov-report=html -vvv'

