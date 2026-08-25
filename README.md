# Calorie Tracker

A calorie tracking web app that uses Claude to estimate meal nutrition from text descriptions and photos.

## Features

- **AI-powered estimation** — describe a meal or upload a photo and get structured macro predictions (kcal, protein, carbs, fat) with confidence levels
- **Daily tracking** — log meals, view daily totals, navigate between days
- **Goals** — set nutritional targets and track progress
- **Copy meals** — copy meals from/to other days to speed up logging
- **Photo support** — attach multiple photos per meal; the LLM reads nutrition labels and estimates from visuals
- **Auth** — registration and login

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.14 |
| Framework | Flask |
| Database | PostgreSQL 16 |
| LLM | Anthropic Claude (Sonnet) |
| ORM | SQLAlchemy + Alembic |
| Package manager | uv |
| Containerization | Docker + Docker Compose |
| Prod server | Gunicorn |
| Frontend | Bootstrap 5 |
| Testing | Pytest |
| Linting | Ruff |

## Getting Started

### Prerequisites

- Docker & Docker Compose
- An [Anthropic API key](https://console.anthropic.com/)

### Environment Variables

```bash
cp .env.sample .env
```

Fill in your values in `.env`.

### Run

```bash
# Development (hot reload)
docker compose up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

The app is available at `http://localhost:8001`.

### Run Without Docker

```bash
uv sync
uv run flask db upgrade
uv run flask run --debug
```

Requires a running PostgreSQL instance and `POSTGRES_HOST` set accordingly.

## Testing

```bash
uv run pytest
```

## Roadmap

1. **Multi-model comparison** — benchmark multiple LLMs on calorie estimation accuracy
2. **OFF database + agentic workflow** — LLM agent with tool access to Open Food Facts; user describes a meal naturally, the agent fetches real product data and computes macros
3. **Agentic vs. naive benchmark** — compare the DB-backed agentic approach against direct LLM estimation
