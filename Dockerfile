FROM python:3.11.0-alpine3.16 as prod-env

RUN apk add --no-cache build-base

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY /src /app/src
COPY /.*-version /app/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]

FROM prod-env as dev-env

RUN apk add --no-cache git bash curl unzip

WORKDIR /usr/bin

RUN RELEASE=$(cat /app/.terraform-version) && \
    wget https://releases.hashicorp.com/terraform/${RELEASE}/terraform_${RELEASE}_linux_amd64.zip && \
    unzip terraform_${RELEASE}_linux_amd64.zip

RUN RELEASE=$(cat /app/.tflint-version) && \
    curl -s https://raw.githubusercontent.com/terraform-linters/tflint/${RELEASE}/install_linux.sh | bash

WORKDIR /app

COPY requirements_dev.txt ./
RUN pip install -r requirements_dev.txt --no-cache-dir
