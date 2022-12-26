FROM python:3.11.0-alpine3.17 as prod-env

WORKDIR /usr/bin/src

COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY app ./app
COPY .*-version ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]

FROM prod-env as dev-env

RUN apk add --no-cache git bash curl unzip

WORKDIR /usr/bin

RUN RELEASE=$(cat src/.terraform-version) && \
    curl -s https://releases.hashicorp.com/terraform/${RELEASE}/terraform_${RELEASE}_linux_amd64.zip | busybox unzip -

RUN RELEASE=$(cat src/.tflint-version) && \
    curl -s https://raw.githubusercontent.com/terraform-linters/tflint/${RELEASE}/install_linux.sh | bash

WORKDIR /usr/bin/src

COPY requirements_dev.txt ./
RUN pip install -r requirements_dev.txt --no-cache-dir
