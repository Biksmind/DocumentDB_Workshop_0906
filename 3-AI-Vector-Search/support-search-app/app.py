r"""Local web app for searching support articles.

Run from the repository root:
    python .\3-AI-Vector-Search\support-search-app\app.py

Then open:
    http://localhost:5050
"""

from __future__ import annotations

import html
import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlparse

from dotenv import load_dotenv
from openai import AzureOpenAI
from pymongo import MongoClient


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing {name}. Create .env in the repository root and fill in the workshop values."
        )
    return value


def normalize_azure_endpoint(value: str) -> str:
    value = value.rstrip("/")
    if value.endswith("/openai/v1"):
        value = value[: -len("/openai/v1")]
    return value


mongo_client = MongoClient(require_env("DOCUMENTDB_CONNECTION_STRING"))
db = mongo_client[os.getenv("DOCUMENTDB_DATABASE", "Workshop_DB")]
openai_client: AzureOpenAI | None = None


SUGGESTIONS = [
    "battery update",
    "my phone loses charge very fast after installing new version",
    "wifi connected but internet not working",
    "bluetooth earbuds keep disconnecting",
    "phone heats up while gaming",
    "notifications are delayed",
    "camera blurry in dark room",
    "payment app fails during checkout",
    "fingerprint unlock not working",
    "storage full phone slow",
]


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocumentDB Support Search</title>
  <style>
    body { font-family: "Segoe UI", Arial, sans-serif; margin: 0; background: #f6f7fb; color: #1f2937; }
    header { background: #172554; color: white; padding: 28px 40px; }
    main { max-width: 1180px; margin: 0 auto; padding: 32px 24px; }
    .panel { background: white; border: 1px solid #e5e7eb; border-radius: 14px; padding: 22px; box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06); }
    form { display: grid; grid-template-columns: minmax(260px, 1fr) 180px 120px; gap: 12px; margin-bottom: 18px; }
    input, select { padding: 12px 14px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 16px; background: white; }
    button { padding: 12px 18px; border: none; border-radius: 10px; background: #2563eb; color: white; font-size: 16px; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    .hint { color: #64748b; line-height: 1.5; }
    .mode-note { background: #eef6ff; border: 1px solid #bfdbfe; color: #1e3a8a; border-radius: 10px; padding: 12px 14px; margin: 16px 0; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 20px; }
    .card { background: white; border: 1px solid #e5e7eb; border-radius: 14px; padding: 18px; }
    .title { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
    .meta { color: #475569; font-size: 14px; margin-bottom: 10px; }
    .tag { display: inline-block; margin: 3px 4px 3px 0; padding: 4px 8px; background: #e2e8f0; border-radius: 999px; font-size: 12px; }
    .score { color: #7c3aed; font-size: 13px; margin-top: 10px; line-height: 1.5; }
    .chip { display: inline-block; margin: 4px; padding: 7px 10px; background: #e2e8f0; color: #0f172a; text-decoration: none; border-radius: 999px; font-size: 14px; }
    .chip:hover { background: #cbd5e1; }
    .empty, .error { padding: 14px; border-radius: 10px; margin-top: 18px; }
    .empty { background: #fff7ed; border: 1px solid #fed7aa; }
    .error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
    code { background: #e2e8f0; padding: 2px 5px; border-radius: 5px; }
    @media (max-width: 850px) { form { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>DocumentDB Support Search Playground</h1>
    <p>Search support articles using full-text, vector, and hybrid search.</p>
  </header>
  <main>
    <section class="panel">
      <form method="get" action="/">
        <input name="q" value="__QUERY__" placeholder="Try: battery drains after update" autofocus>
        <select name="mode">__MODE_OPTIONS__</select>
        <button type="submit">Search</button>
      </form>
      <p class="hint">This support dataset is better for explaining search behavior because the expected articles are less subjective.</p>
      __CONTENT__
    </section>
  </main>
</body>
</html>"""


def get_openai_client() -> AzureOpenAI:
    global openai_client
    if openai_client is None:
        openai_client = AzureOpenAI(
            azure_endpoint=normalize_azure_endpoint(require_env("AZURE_OPENAI_ENDPOINT")),
            api_key=require_env("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        )
    return openai_client


def generate_embedding(text: str) -> list[float]:
    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "256"))
    response = get_openai_client().embeddings.create(
        model=deployment,
        input=text,
        dimensions=dimensions,
    )
    return response.data[0].embedding


def projection() -> dict:
    return {
        "articleId": 1,
        "title": 1,
        "product": 1,
        "category": 1,
        "severity": 1,
        "content": 1,
        "tags": 1,
        "_id": 0,
    }


def search_full_text(query: str, limit: int = 10) -> list[dict]:
    results = list(
        db.support_articles.find(
            {"$text": {"$search": query}},
            {**projection(), "textScore": {"$meta": "textScore"}},
        )
        .sort([("textScore", {"$meta": "textScore"})])
        .limit(limit)
    )
    for result in results:
        result["source"] = "Full-text"
    return results


def search_vector(query: str, limit: int = 10) -> list[dict]:
    ensure_support_vector_ready()
    query_vector = generate_embedding(query)
    results = list(
        db.support_articles.aggregate(
            [
                {
                    "$search": {
                        "cosmosSearch": {
                            "vector": query_vector,
                            "path": "contentVector",
                            "k": limit,
                        }
                    }
                },
                {"$project": {**projection(), "vectorScore": {"$meta": "searchScore"}}},
            ]
        )
    )
    for result in results:
        result["source"] = "Vector"
    return results


def ensure_support_vector_ready() -> None:
    sample = db.support_articles.find_one(
        {"contentVector": {"$exists": True}},
        {"_id": 0, "articleId": 1},
    )
    indexes = {index["name"] for index in db.support_articles.list_indexes()}
    if sample and "support_vector_index" in indexes:
        return

    raise RuntimeError(
        "Support vector search is not ready yet. Run these commands from the repository root:\n"
        "python .\\3-AI-Vector-Search\\support-data\\generate_support_embeddings.py\n"
        "python .\\scripts\\load_workshop_data.py\n"
        "python .\\scripts\\validate_workshop_setup.py"
    )


def search_hybrid(query: str, limit: int = 10) -> list[dict]:
    text_results = search_full_text(query, limit=20)
    vector_results = search_vector(query, limit=20)
    combined: dict[str, dict] = {}
    k = 60

    for rank, result in enumerate(text_results, 1):
        key = result["articleId"]
        combined.setdefault(key, result.copy())
        combined[key]["textRank"] = rank
        combined[key]["textScore"] = float(result.get("textScore", 0))
        combined[key]["hybridScore"] = combined[key].get("hybridScore", 0) + 1 / (k + rank)

    for rank, result in enumerate(vector_results, 1):
        key = result["articleId"]
        combined.setdefault(key, result.copy())
        combined[key]["vectorRank"] = rank
        combined[key]["vectorScore"] = float(result.get("vectorScore", 0))
        combined[key]["hybridScore"] = combined[key].get("hybridScore", 0) + 1 / (k + rank)

    return sorted(combined.values(), key=lambda item: item.get("hybridScore", 0), reverse=True)[:limit]


def run_search(mode: str, query: str) -> list[dict]:
    if mode == "vector":
        return search_vector(query)
    if mode == "hybrid":
        return search_hybrid(query)
    return search_full_text(query)


def mode_options(selected: str) -> str:
    modes = [("fulltext", "Full-text"), ("vector", "Vector"), ("hybrid", "Hybrid")]
    return "\n".join(
        f'<option value="{value}" {"selected" if selected == value else ""}>{label}</option>'
        for value, label in modes
    )


def mode_note(mode: str) -> str:
    notes = {
        "fulltext": "Full-text is best for exact words like battery, update, Wi-Fi, or Bluetooth.",
        "vector": "Vector search is best for natural language like 'my phone loses charge very fast after installing new version'.",
        "hybrid": "Hybrid search combines exact keyword matching with semantic similarity.",
    }
    return f'<div class="mode-note">{notes.get(mode, notes["fulltext"])}</div>'


def score_text(result: dict, mode: str) -> str:
    if mode == "hybrid":
        return (
            f"Hybrid score: {result.get('hybridScore', 0):.4f}<br>"
            f"Text rank: {result.get('textRank', '-')} · Vector rank: {result.get('vectorRank', '-')}"
        )
    if mode == "vector":
        return f"Vector score: {result.get('vectorScore', 0):.4f}"
    return f"Text score: {result.get('textScore', 0):.2f}"


def render_card(article: dict, mode: str) -> str:
    tags = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in article.get("tags", []))
    return f"""
    <article class="card">
      <div class="title">{html.escape(article.get("title", ""))}</div>
      <div class="meta">{html.escape(article.get("articleId", ""))} · {html.escape(article.get("category", ""))} · Severity: {html.escape(article.get("severity", ""))}</div>
      <p>{html.escape(article.get("content", ""))}</p>
      <div>{tags}</div>
      <div class="score">{score_text(article, mode)}</div>
    </article>
    """


def suggestion_links(mode: str) -> str:
    links = [
        f'<a class="chip" href="/?q={quote_plus(prompt)}&mode={mode}">{html.escape(prompt)}</a>'
        for prompt in SUGGESTIONS
    ]
    return '<p class="hint">Try these searches:</p>' + "".join(links)


def render_results(query: str, mode: str) -> str:
    intro = mode_note(mode)
    if not query:
        return intro + suggestion_links(mode)

    try:
        results = run_search(mode, query)
    except Exception as error:
        return (
            intro
            + f'<div class="error"><strong>Search failed.</strong><br>{html.escape(str(error))}</div>'
            + suggestion_links(mode)
        )

    if not results:
        return (
            intro
            + f'<div class="empty">No support articles found for <strong>{html.escape(query)}</strong>.</div>'
            + suggestion_links(mode)
        )

    cards = "".join(render_card(article, mode) for article in results)
    return (
        intro
        + f"<p>Showing {len(results)} {mode} result(s) for <strong>{html.escape(query)}</strong>.</p>"
        + f'<div class="grid">{cards}</div>'
        + suggestion_links(mode)
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/", "/health"}:
            self.send_error(404)
            return

        if parsed.path == "/health":
            self._send_json({"ok": True})
            return

        params = parse_qs(parsed.query)
        query = params.get("q", [""])[0].strip()
        mode = params.get("mode", ["fulltext"])[0].strip().lower()
        if mode not in {"fulltext", "vector", "hybrid"}:
            mode = "fulltext"

        page = (
            PAGE.replace("__QUERY__", html.escape(query))
            .replace("__MODE_OPTIONS__", mode_options(mode))
            .replace("__CONTENT__", render_results(query, mode))
        )
        self._send_html(page)

    def _send_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, body: dict) -> None:
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    host = "localhost"
    port = 5050
    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print("DocumentDB Support Search Playground is running.")
    print(f"Open: {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
