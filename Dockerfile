FROM python:3.10-slim-buster AS base

RUN mkdir -p /users_db
RUN mkdir -p /tests
RUN mkdir -p /scripts

COPY ./users_db /users_db/
COPY ./tests /tests/
COPY ./scripts /scripts/
COPY ./pyproject.toml /
COPY ./poetry.lock /
COPY ./README.md /

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install poetry==1.4.0
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# install users_db as editable
RUN pip install -e ./

# set work directory
WORKDIR /users_db

FROM base AS development
CMD [ "/scripts/migrate_start.sh" ]

# TODO prod/test image to run in CI/CD pipeline 
# with integration tests