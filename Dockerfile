ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY . /app

RUN pip install poetry && poetry install
