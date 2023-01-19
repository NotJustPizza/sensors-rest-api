FROM python:3.11.1-alpine3.17 as base-env

WORKDIR /usr/bin/src
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

CMD ["uvicorn", "app.run:app", "--host", "0.0.0.0"]

FROM base-env as prod-env

COPY app ./app

FROM base-env as dev-env

WORKDIR /usr/bin
RUN apk add --no-cache git wget bash

COPY .terraform-version ./src/
RUN TF_VERSION=$(cat src/.terraform-version) && \
    wget -q https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip && \
    unzip terraform_${TF_VERSION}_linux_amd64.zip && \
    rm terraform_${TF_VERSION}_linux_amd64.zip

ENV TFLINT_VERSION="0.44.1"
RUN wget -q https://github.com/terraform-linters/tflint/releases/download/v${TFLINT_VERSION}/tflint_linux_amd64.zip && \
    unzip tflint_linux_amd64.zip && \
    rm tflint_linux_amd64.zip

ENV TFSEC_VERSION="1.28.1"
RUN wget -q https://github.com/aquasecurity/tfsec/releases/download/v${TFSEC_VERSION}/tfsec_${TFSEC_VERSION}_linux_amd64.tar.gz && \
    tar xzf tfsec_${TFSEC_VERSION}_linux_amd64.tar.gz && \
    rm tfsec_${TFSEC_VERSION}_linux_amd64.tar.gz

ENV TERRASCAN_VERSION="1.17.1"
RUN wget -q https://github.com/tenable/terrascan/releases/download/v${TERRASCAN_VERSION}/terrascan_${TERRASCAN_VERSION}_Linux_arm64.tar.gz && \
    tar xzf terrascan_${TERRASCAN_VERSION}_Linux_arm64.tar.gz && \
    rm terrascan_${TERRASCAN_VERSION}_Linux_arm64.tar.gz

WORKDIR /usr/bin/src
COPY requirements_dev.txt ./
RUN pip install -r requirements_dev.txt --no-cache-dir
