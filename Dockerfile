FROM python:3.10-slim-buster

RUN mkdir -p /code

COPY ./poetry.lock /
COPY ./pyproject.toml /
COPY ./ /users_db

RUN pip install poetry==1.4.0
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt
RUN pip install -e /users_db

WORKDIR /users_db
CMD ["./scripts/migrate_start.sh"]
