FROM python:3.11.0-alpine3.16 as prod-env

RUN apk add --no-cache build-base

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY /src /app/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]

FROM prod-env as dev-env

RUN apk add --no-cache git bash

COPY requirements_dev.txt ./
RUN pip install -r requirements_dev.txt --no-cache-dir
