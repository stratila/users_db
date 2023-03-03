FROM python:3.10-slim-buster

ADD ./ /
RUN pip install poetry==1.4.0
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt
RUN pip install -e /.

CMD ["./scripts/migrate_start.sh"]
