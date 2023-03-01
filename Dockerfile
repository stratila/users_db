FROM python:3.10-slim-buster

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /users_db
COPY ./ /users_db

RUN pip install -e /users_db

WORKDIR /users_db
CMD ["./scripts/migrate_start.sh"]
