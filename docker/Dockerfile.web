# checkov:skip=CKV_DOCKER_3:It is non-trival to configure non-root user for this image due to required project mount.
FROM python:3.11.2-alpine3.17 as python

FROM python as poetry

WORKDIR /opt/poetry
ENV POETRY_VERSION="1.4.1"
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$PATH:$POETRY_HOME/bin"
ENV POETRY_VIRTUALENVS_PATH="$POETRY_HOME/venvs"
RUN wget -q https://install.python-poetry.org -O install-poetry.py
RUN python3 install-poetry.py
RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.options.always-copy true
RUN poetry config virtualenvs.options.no-pip true
RUN poetry config virtualenvs.options.no-setuptools true

FROM poetry as prod-builder

WORKDIR /opt/src
COPY pyproject.toml poetry.lock ./
RUN poetry install --compile --no-cache

FROM python as prod-env

WORKDIR /opt/src
COPY --from=prod-builder /opt/src/.venv .venv
ENV PATH="/opt/src/.venv/bin:$PATH"

COPY app ./app
CMD ["uvicorn", "app.run:app", "--host", "0.0.0.0"]
HEALTHCHECK CMD curl --fail http://localhost/actions/healthcheck || exit 1

FROM poetry as dev-tools

WORKDIR /usr/bin
RUN apk add --no-cache git bash

COPY .terraform-version ./src/
RUN TF_VERSION=$(cat src/.terraform-version) && \
    wget -q https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip && \
    unzip terraform_${TF_VERSION}_linux_amd64.zip && \
    rm terraform_${TF_VERSION}_linux_amd64.zip

ENV TFLINT_VERSION="0.45.0"
RUN wget -q https://github.com/terraform-linters/tflint/releases/download/v${TFLINT_VERSION}/tflint_linux_amd64.zip && \
    unzip tflint_linux_amd64.zip && \
    rm tflint_linux_amd64.zip

ENV TFSEC_VERSION="1.28.1"
RUN wget -q https://github.com/aquasecurity/tfsec/releases/download/v${TFSEC_VERSION}/tfsec_${TFSEC_VERSION}_linux_amd64.tar.gz && \
    tar xzf tfsec_${TFSEC_VERSION}_linux_amd64.tar.gz && \
    rm tfsec_${TFSEC_VERSION}_linux_amd64.tar.gz

WORKDIR /opt/src
COPY pyproject.toml poetry.lock ./
RUN poetry install --compile --no-cache --with dev
ENV PATH="/opt/src/.venv/bin:$PATH"
