ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim
WORKDIR /opt/app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install
COPY . .
