#!/bin/sh

python /scripts/check_postgres_accept_connections.py
alembic_upgrade 
pytest /tests
tail -f /dev/null