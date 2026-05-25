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

```bash
docker build -t afp-rss .
docker run -d -p 8080:8080 --name afp-rss afp-rss
```
