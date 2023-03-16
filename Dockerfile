FROM python:3.10-slim-buster AS base

RUN mkdir -p /users_db
RUN mkdir -p /tests

COPY ./users_db /users_db/
COPY ./tests /tests/
COPY ./pyproject.toml /
COPY ./poetry.lock /
COPY ./README.md /

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install poetry==1.4.0
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
# install users_db as editable
RUN pip install -e ./
