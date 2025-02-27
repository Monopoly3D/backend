ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim

WORKDIR /opt/app

COPY . .

RUN pip install poetry && poetry install
