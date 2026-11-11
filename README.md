# Monopoly 3D Backend

Backend server for Monopoly 3D, an online multiplayer board game. Players sign up, create or join a game over HTTP, then play in real time over a WebSocket connection.

## Features

- **Real-time gameplay** over WebSockets with a typed packet protocol: 19 client packets (move, buy, auction, mortgage, casino, prison, kick...) and 40 server packets.
- **Game state in Redis** for active games, players and connections; PostgreSQL for users and accounts.
- **Full game domain**: properties and companies, monopolies and branches, auctions, mortgages, rent, taxes, chance cards, casino and prison, with typed domain errors returned to clients.
- **Auth**: registration with email verification, JWT access tokens and refresh tokens (stored in their own table, sent as an HTTP-only cookie), Argon2 password hashing, user roles.
- **WebSocket auth** through short-lived game tickets issued over HTTP.
- **Profile pictures** stored in S3-compatible storage (MinIO locally).
- **CI/CD**: GitHub Actions builds a Docker image, pushes it to GHCR and deploys it.

## Stack

Python 3.13 · FastAPI · WebSockets · Pydantic · SQLAlchemy 2 (async) · Alembic · PostgreSQL · Redis · aiobotocore · PyJWT · Argon2 · pytest · Docker

## Project layout

```
app/
  api/v1/routes/http/        auth, users, games (REST)
  api/v1/routes/websocket/   game connection and packet dispatch
  api/v1/packets/            client and server packet models
  assets/objects/            game, players, fields and actions
  assets/redis/              Redis repositories for live state
  database/                  SQLAlchemy models
migrations/                  Alembic migrations
tests/                       pytest suite
```

## Running locally

Requirements: Python 3.13, Poetry, Docker.

```bash
# Postgres, Redis and MinIO
docker compose -f compose-local.yaml up -d

# Dependencies
poetry install

# Fill .env (api_key, jwt_key, database_dsn, redis_dsn, s3_dsn, s3_username, s3_password, optional SMTP settings)

# Database schema
alembic upgrade head

# API on :8000
python main.py
```

The 3D web client lives in a separate repository; the game frontend was built by my teammate.
