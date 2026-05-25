FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml ./

RUN uv sync --no-dev

COPY main.py ./

EXPOSE 8080

CMD ["uv", "run", "python", "main.py"]