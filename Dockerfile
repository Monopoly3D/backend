ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim
WORKDIR /opt/app
RUN apt-get update && apt-get install gcc g++ curl build-essential postgresql-server-dev-all -y
COPY . .
RUN pip install poetry && poetry install
