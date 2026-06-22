FROM python:3.14-slim

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /uvx /bin/

# Install dependencies first (better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --group prod --frozen --no-dev

# Copy source
COPY app/ ./app/
COPY config.py wsgi.py ./

EXPOSE 8001
CMD ["uv", "run", "--no-dev", "gunicorn", "--bind", "0.0.0.0:8001", "wsgi:app"]
