# AFP RSS Feeds

A simple, lightweight scraper that fetches the latest AFP news from Mediapart and exposes them as Atom, JSON, and plain text feeds. It updates automatically in the background every hour.

## Endpoints

Once the server is running on port 8080, you can access:
- `http://localhost:8080/rss.atom`
- `http://localhost:8080/rss.json`
- `http://localhost:8080/rss.txt`

## Running Locally

This project uses `uv` for dependency management:

```bash
uv sync
uv run python main.py
```

## Running with Docker

You can use the pre-built image directly from Docker Hub:

```bash
docker run -d -p 8080:8080 --name afp-rss nohamr/afp-rss:latest
```

### Using Docker Compose

A `docker-compose.yml` file is provided for convenience:

```bash
docker compose up -d
```

### Building the Image Yourself

```bash
docker build -t afp-rss .
docker run -d -p 8080:8080 --name afp-rss afp-rss
```