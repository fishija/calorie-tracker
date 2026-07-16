# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Base: shared by dev and prod. Installs uv and dependency manifests only,
# so this layer stays cached as long as pyproject.toml/uv.lock don't change.
# ---------------------------------------------------------------------------
FROM python:3.14-slim AS base

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./


# ---------------------------------------------------------------------------
# Development: installs dev dependency group, source is bind-mounted at
# runtime (see docker-compose.override.yml), so COPY . . here mostly matters
# for one-off `docker build` runs without compose.
# ---------------------------------------------------------------------------
FROM base AS development

RUN uv sync --frozen

COPY . .

EXPOSE 8001

CMD ["uv", "run", "flask", "run", "--host", "0.0.0.0", "--port", "8001", "--debug"]


# ---------------------------------------------------------------------------
# Production: installs prod dependency group only (no dev/test tooling),
# copies just what's needed to run the app - smaller image, no stray files.
# ---------------------------------------------------------------------------
FROM base AS production

RUN uv sync --group prod --frozen --no-dev

COPY app/ ./app/
COPY config.py wsgi.py ./
COPY migrations/ ./migrations/

EXPOSE 8001

CMD ["uv", "run", "--no-dev", "gunicorn", "--bind", "0.0.0.0:8001", "wsgi:app"]