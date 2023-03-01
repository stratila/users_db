#!/bin/sh

python scripts/check_postgres_accept_connections.py
alembic upgrade head
pytest 
tail -f /dev/null