FROM python:3.11.0-alpine3.17 as base-env

WORKDIR /usr/bin/src
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

CMD ["uvicorn", "app.run:app", "--host", "0.0.0.0"]

FROM base-env as prod-env

WORKDIR /usr/bin/src
COPY app ./app

FROM base-env as dev-env

WORKDIR /usr/bin
RUN apk add --no-cache git bash curl unzip
COPY .*-version ./src/

RUN RELEASE=$(cat src/.terraform-version) && \
    curl -s https://releases.hashicorp.com/terraform/${RELEASE}/terraform_${RELEASE}_linux_amd64.zip | busybox unzip -
RUN chmod 0755 terraform

RUN RELEASE=$(cat src/.tflint-version) && \
    curl -s https://raw.githubusercontent.com/terraform-linters/tflint/${RELEASE}/install_linux.sh | bash

WORKDIR /usr/bin/src
COPY requirements_dev.txt ./
RUN pip install -r requirements_dev.txt --no-cache-dir
