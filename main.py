import time
import json
import threading
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup

news_list = []
LAST_UPDATE = ""


def fetch_news():
    global news_list, LAST_UPDATE
    session = requests.Session()
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    }

    try:
        response = session.get(
            "https://www.mediapart.fr/journal/fil-dactualites", headers=headers
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("div", class_="teaser")

        new_news_list = []
        for article in articles:
            title_tag = article.find("h2", class_="teaser__title")
            titre = (
                title_tag.get_text(separator=" ", strip=True)
                if title_tag
                else "Non trouvé"
            )

            body_tag = article.find("div", class_="teaser__body")
            resume = (
                body_tag.get_text(separator=" ", strip=True)
                if body_tag
                else "Non trouvé"
            )

            date_tag = article.find("time", class_="teaser__timestamp")
            date_iso = (
                date_tag.get("datetime", datetime.now(timezone.utc).isoformat())
                if date_tag
                else datetime.now(timezone.utc).isoformat()
            )

            link_tag = article.find("a")
            link = (
                f"https://www.mediapart.fr{link_tag['href']}"
                if link_tag and "href" in link_tag.attrs
                else "https://www.mediapart.fr"
            )

            # Use link as id
            new_news_list.append(
                {
                    "title": titre,
                    "content": resume,
                    "date_modified": date_iso,
                    "url": link,
                    "id": link,
                }
            )

        news_list = new_news_list
        LAST_UPDATE = datetime.now(timezone.utc).isoformat()
        print(f"[{LAST_UPDATE}] News fetched successfully ({len(news_list)} items).")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Error fetching news: {e}")


def update_loop():
    while True:
        fetch_news()
        time.sleep(3600)  # Update periodically (every hour)


def build_atom():
    fg = FeedGenerator()
    fg.id("https://www.mediapart.fr/journal/fil-dactualites")
    fg.title("Mediapart Fil d'actualités")
    fg.author({"name": "Mediapart"})
    fg.link(href="https://www.mediapart.fr", rel="alternate")
    fg.updated(LAST_UPDATE)

    for item in news_list:
        fe = fg.add_entry()
        fe.id(item["id"])
        fe.title(item["title"])
        fe.link(href=item["url"], rel="alternate")
        fe.published(item["date_modified"])
        fe.updated(item["date_modified"])
        fe.content(item["content"], type="html")

    return fg.atom_str(pretty=True)


def build_json():
    data = {
        "version": "https://jsonfeed.org/version/1",
        "title": "Mediapart Fil d'actualités",
        "home_page_url": "https://www.mediapart.fr",
        "items": [
            {
                "id": item["id"],
                "title": item["title"],
                "date_modified": item["date_modified"],
                "url": item["url"],
                "content_text": item["content"],
            }
            for item in news_list
        ],
    }
    return json.dumps(data, indent=4).encode("utf-8")


def build_txt():
    # Emulate PHP print_r output for text like in the example
    lines = []
    lines.append("Array")
    lines.append("(")
    lines.append("    [name] => Mediapart Fil d'actualités")
    lines.append("    [uri] => https://www.mediapart.fr")
    lines.append("    [items] => Array")
    lines.append("        (")

    for i, item in enumerate(news_list):
        lines.append(f"            [{i}] => Array")
        lines.append("                (")
        lines.append(f"                    [uri] => {item['url']}")
        lines.append(f"                    [title] => {item['title']}")
        lines.append(f"                    [timestamp] => {item['date_modified']}")
        lines.append(f"                    [content] => {item['content']}")
        lines.append("                )")
        lines.append("")

    lines.append("        )")
    lines.append(")")
    return "\n".join(lines).encode("utf-8")


class RSSRequestHandler(BaseHTTPRequestHandler):
    # Hide log requests to not spam console
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/rss.atom":
            self.send_response(200)
            self.send_header("Content-Type", "application/atom+xml; charset=utf-8")
            self.end_headers()
            self.wfile.write(build_atom())
        elif self.path == "/rss.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(build_json())
        elif self.path == "/rss.txt":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(build_txt())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html><body>
                <h1>Mediapart RSS</h1>
                <ul>
                    <li><a href="/rss.atom">Atom Feed</a></li>
                    <li><a href="/rss.json">JSON Feed</a></li>
                    <li><a href="/rss.txt">Plaintext Feed</a></li>
                </ul>
            </body></html>
            """
            self.wfile.write(html.encode("utf-8"))


def main():
    print("Starting initial fetch...")
    fetch_news()

    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()

    server_address = ("", 8080)
    httpd = HTTPServer(server_address, RSSRequestHandler)
    print("Serving feeds at port 8080.")
    print(
        "Paths available: http://localhost:8080/rss.atom, http://localhost:8080/rss.json, http://localhost:8080/rss.txt"
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    main()
