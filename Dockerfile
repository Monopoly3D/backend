ARG PYTHON_VERSION=3.13
ARG POETRY_VERSION=1.8.5

FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY . .

RUN pip install poetry==${POETRY_VERSION} && poetry install
