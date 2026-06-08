r"""Small local web app for searching the mobile catalog.

Run from the repository root:
    python .\3-AI-Vector-Search\mobile-search-app\app.py

Then open:
    http://localhost:5000
"""

from __future__ import annotations

import html
import json
import os
import re
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


SUGGESTIONS = {
    "Camera": [
        "camera performance 5G",
        "photography smartphone 5G",
        "best camera battery phone",
        "camera focused smartphone",
        "travel photography phone",
    ],
    "Battery": [
        "battery backup 5G phone",
        "long battery life smartphone",
        "all day battery 5G",
        "battery monster smartphone",
        "camera battery champion",
    ],
    "Gaming": [
        "gaming smartphone 5G",
        "high performance gaming phone",
        "smooth gaming fast charging",
        "lag free gaming smartphone",
        "student gaming smartphone",
    ],
    "Budget": [
        "affordable 5G smartphone",
        "budget friendly 5G phone",
        "student budget smartphone",
        "value for money 5G",
        "entry level 5G device",
    ],
    "Premium": [
        "flagship camera smartphone",
        "premium photography phone",
        "premium performance smartphone",
        "premium multimedia phone",
        "fast charging flagship",
    ],
    "Mixed": [
        "camera battery 5G",
        "gaming camera phone",
        "student gaming budget",
        "premium battery flagship",
        "budget gaming 5G",
    ],
}

FULL_TEXT_EXPANSIONS = {
    "mobile": ["phone", "smartphone", "5G"],
    "mobiles": ["phone", "smartphone", "5G"],
    "phone": ["mobile", "smartphone"],
    "phones": ["mobile", "smartphone"],
    "smartphone": ["phone", "mobile"],
    "smartphones": ["phone", "mobile"],
    "cheap": ["budget", "affordable", "value"],
    "affordable": ["budget", "value"],
    "student": ["budget", "affordable", "5G"],
    "photo": ["camera", "photography"],
    "photos": ["camera", "photography"],
    "picture": ["camera", "photography"],
    "pictures": ["camera", "photography"],
    "night": ["camera", "photography", "low light"],
    "game": ["gaming", "performance"],
    "games": ["gaming", "performance"],
    "office": ["productivity", "business", "performance"],
    "work": ["productivity", "business", "performance"],
    "travel": ["camera", "battery", "photography"],
}

SEMANTIC_INTENT_EXPANSIONS = {
    "budget": [
        "affordable 5G smartphone",
        "budget friendly 5G phone",
        "student budget smartphone",
        "value for money 5G",
        "entry level 5G device",
    ],
    "camera": [
        "camera performance 5G",
        "photography smartphone 5G",
        "best camera battery phone",
        "camera focused smartphone",
        "travel photography phone",
    ],
    "battery": [
        "battery backup 5G phone",
        "long battery life smartphone",
        "all day battery 5G",
        "battery monster smartphone",
        "camera battery champion",
    ],
    "gaming": [
        "gaming smartphone 5G",
        "high performance gaming phone",
        "smooth gaming fast charging",
        "fast charging gaming device",
        "lag free gaming smartphone",
    ],
    "premium": [
        "flagship camera smartphone",
        "premium photography phone",
        "high end camera device",
        "flagship 5G experience",
        "premium performance smartphone",
    ],
    "creator": [
        "content creator smartphone",
        "creator focused smartphone",
        "premium multimedia phone",
        "travel photography phone",
    ],
    "student": [
        "student budget smartphone",
        "college student smartphone",
        "student friendly 5G device",
        "student gaming smartphone",
    ],
    "family": [
        "reliable phone for parents",
        "easy to use smartphone",
        "simple phone with long battery",
        "large display smartphone for daily use",
        "phone for calls and WhatsApp",
    ],
    "office": [
        "business productivity smartphone",
        "phone for office work",
        "reliable calling smartphone",
        "clean software productivity phone",
        "multitasking 5G smartphone",
    ],
    "travel": [
        "travel photography phone",
        "phone with camera and long battery",
        "compact travel smartphone",
        "reliable phone for trips",
        "all day battery camera phone",
    ],
    "reliable": [
        "reliable daily use smartphone",
        "simple clean software phone",
        "long battery everyday phone",
        "durable value smartphone",
        "easy to use 5G phone",
    ],
}


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocumentDB Mobile Search</title>
  <style>
    body {
      font-family: "Segoe UI", Arial, sans-serif;
      margin: 0;
      background: #f5f7fb;
      color: #1f2937;
    }
    header {
      background: #0f172a;
      color: white;
      padding: 28px 40px;
    }
    header p {
      max-width: 900px;
      line-height: 1.5;
    }
    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 24px;
    }
    .panel {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      padding: 22px;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }
    form {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) 180px 120px;
      gap: 12px;
      margin-bottom: 18px;
    }
    input, select {
      padding: 12px 14px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      font-size: 16px;
      background: white;
    }
    button {
      padding: 12px 18px;
      border: none;
      border-radius: 10px;
      background: #2563eb;
      color: white;
      font-size: 16px;
      cursor: pointer;
    }
    button:hover {
      background: #1d4ed8;
    }
    .hint {
      color: #64748b;
      margin-top: 0;
      line-height: 1.5;
    }
    .mode-note {
      background: #eef6ff;
      border: 1px solid #bfdbfe;
      color: #1e3a8a;
      border-radius: 10px;
      padding: 12px 14px;
      margin: 16px 0;
    }
    .suggestions {
      margin-top: 18px;
    }
    .suggestion-group {
      margin: 12px 0;
    }
    .suggestion-group strong {
      display: inline-block;
      min-width: 80px;
    }
    .chip {
      display: inline-block;
      margin: 4px;
      padding: 7px 10px;
      background: #e2e8f0;
      color: #0f172a;
      text-decoration: none;
      border-radius: 999px;
      font-size: 14px;
    }
    .chip:hover {
      background: #cbd5e1;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-top: 20px;
    }
    .card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      padding: 18px;
    }
    .title {
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .meta {
      color: #475569;
      font-size: 14px;
      margin-bottom: 10px;
    }
    .price {
      font-weight: 700;
      color: #047857;
    }
    .score {
      color: #7c3aed;
      font-size: 13px;
      margin-top: 10px;
      line-height: 1.5;
    }
    .empty, .error {
      padding: 14px;
      border-radius: 10px;
      margin-top: 18px;
    }
    .empty {
      background: #fff7ed;
      border: 1px solid #fed7aa;
    }
    .error {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #991b1b;
    }
    code {
      background: #e2e8f0;
      padding: 2px 5px;
      border-radius: 5px;
    }
    @media (max-width: 850px) {
      form {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>DocumentDB Mobile Search Playground</h1>
    <p>
      Try the same mobile catalog with full-text search, vector search, and hybrid search.
      This is a local demo app connected to your Azure DocumentDB cluster.
    </p>
  </header>
  <main>
    <section class="panel">
      <form method="get" action="/">
        <input name="q" value="__QUERY__" placeholder="Try: camera phone battery 5G" autofocus>
        <select name="mode" title="Search mode">
          __MODE_OPTIONS__
        </select>
        <button type="submit">Search</button>
      </form>
      <p class="hint">
        Type anything. The suggestions are only examples, not hardcoded filters.
        Price phrases like <strong>under 15000</strong> are detected automatically.
        Use <strong>Full-text</strong> for keyword matching, <strong>Vector</strong> for meaning,
        and <strong>Hybrid</strong> to combine both.
      </p>
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


def base_projection() -> dict:
    return {
        "title": 1,
        "brand": 1,
        "segment": 1,
        "description": 1,
        "priceInr": 1,
        "rating": 1,
        "cameraMp": 1,
        "batteryMah": 1,
        "_id": 0,
    }


def price_filter(max_price: int | None) -> dict:
    if max_price is None:
        return {}
    return {"priceInr": {"$lte": max_price}}


def infer_max_price(query: str) -> int | None:
    normalized = query.lower().replace(",", "")
    patterns = [
        r"\bunder\s+(?:inr|rs\.?|₹)?\s*(\d+)\b",
        r"\bbelow\s+(?:inr|rs\.?|₹)?\s*(\d+)\b",
        r"\bless\s+than\s+(?:inr|rs\.?|₹)?\s*(\d+)\b",
        r"\bwithin\s+(?:inr|rs\.?|₹)?\s*(\d+)\b",
        r"<=\s*(?:inr|rs\.?|₹)?\s*(\d+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            return int(match.group(1))
    return None


def expand_full_text_query(query: str) -> str:
    terms = re.findall(r"[A-Za-z0-9]+", query.lower())
    expanded_terms: list[str] = []
    for term in terms:
        expanded_terms.extend(FULL_TEXT_EXPANSIONS.get(term, []))

    if not expanded_terms:
        return query

    return " ".join([query, *expanded_terms])


def detect_semantic_intents(query: str) -> set[str]:
    normalized = query.lower()
    terms = set(re.findall(r"[a-z0-9]+", normalized))
    intents: set[str] = set()

    if terms & {"cheap", "budget", "affordable", "value"}:
        intents.add("budget")
    if re.search(r"\bunder\s+\d+", normalized) or re.search(r"\bbelow\s+\d+", normalized):
        intents.add("budget")
    if terms & {"camera", "photo", "photos", "photography", "portrait", "selfie", "creator"}:
        intents.add("camera")
    if terms & {"battery", "backup", "power", "charging"}:
        intents.add("battery")
    if terms & {"gaming", "game", "games", "performance", "lag"}:
        intents.add("gaming")
    if terms & {"premium", "flagship", "luxury", "high", "end"}:
        intents.add("premium")
    if terms & {"creator", "content", "video", "multimedia"}:
        intents.add("creator")
    if terms & {"student", "college"}:
        intents.add("student")
    if terms & {"father", "mother", "parent", "parents", "dad", "mom", "senior", "elder", "elderly"}:
        intents.update({"family", "reliable", "battery"})
    if "office" in terms or "work" in terms or "business" in terms:
        intents.update({"office", "reliable", "battery"})
    if terms & {"whatsapp", "calls", "calling", "simple", "easy"}:
        intents.update({"family", "reliable"})
    if terms & {"travel", "trip", "vacation"}:
        intents.update({"travel", "camera", "battery"})
    if terms & {"mobile", "mobiles", "phone", "phones", "smartphone", "smartphones"} and not intents:
        intents.update({"budget", "camera", "battery"})

    return intents


def expand_semantic_query(query: str) -> str:
    intents = detect_semantic_intents(query)
    phrases: list[str] = []
    for intent in sorted(intents):
        phrases.extend(SEMANTIC_INTENT_EXPANSIONS[intent])

    if not phrases:
        return query

    # Keep the user's original words first, then add curated workshop phrases.
    return " | ".join([query, *phrases])


def search_full_text(query: str, max_price: int | None, limit: int = 12) -> list[dict]:
    expanded_query = expand_full_text_query(query)
    find_filter = {"$text": {"$search": expanded_query}, **price_filter(max_price)}
    projection = {**base_projection(), "textScore": {"$meta": "textScore"}}
    results = list(
        db.mobiles.find(find_filter, projection)
        .sort([("textScore", {"$meta": "textScore"})])
        .limit(limit)
    )
    for result in results:
        result["modeScore"] = float(result.get("textScore", 0))
        result["source"] = "Full-text"
    return results


def search_vector(query: str, max_price: int | None, limit: int = 12) -> list[dict]:
    expanded_query = expand_semantic_query(query)
    query_vector = generate_embedding(expanded_query)
    cosmos_search = {
        "vector": query_vector,
        "path": "contentVector",
        "k": limit,
    }
    if max_price is not None:
        cosmos_search["filter"] = {"priceInr": {"$lte": max_price}}

    results = list(
        db.mobiles.aggregate(
            [
                {"$search": {"cosmosSearch": cosmos_search}},
                {
                    "$project": {
                        **base_projection(),
                        "vectorScore": {"$meta": "searchScore"},
                    }
                },
                {"$limit": limit},
            ]
        )
    )
    for result in results:
        result["modeScore"] = float(result.get("vectorScore", 0))
        result["source"] = "Vector"
        result["expandedQuery"] = expanded_query
    return results


def search_hybrid(query: str, max_price: int | None, limit: int = 12) -> list[dict]:
    text_results = search_full_text(query, max_price, limit=20)
    vector_results = search_vector(query, max_price, limit=20)

    combined: dict[str, dict] = {}
    k = 60

    for rank, result in enumerate(text_results, 1):
        key = result["title"]
        combined.setdefault(key, result.copy())
        combined[key]["textRank"] = rank
        combined[key]["textScore"] = float(result.get("textScore", 0))
        combined[key]["hybridScore"] = combined[key].get("hybridScore", 0) + 1 / (k + rank)

    for rank, result in enumerate(vector_results, 1):
        key = result["title"]
        combined.setdefault(key, result.copy())
        combined[key]["vectorRank"] = rank
        combined[key]["vectorScore"] = float(result.get("vectorScore", 0))
        combined[key]["hybridScore"] = combined[key].get("hybridScore", 0) + 1 / (k + rank)

    results = sorted(
        combined.values(),
        key=lambda item: item.get("hybridScore", 0),
        reverse=True,
    )[:limit]

    for result in results:
        result["source"] = "Hybrid"
        result["modeScore"] = float(result.get("hybridScore", 0))
    return results


def run_search(mode: str, query: str, max_price: int | None) -> list[dict]:
    if mode == "vector":
        return search_vector(query, max_price)
    if mode == "hybrid":
        return search_hybrid(query, max_price)
    return search_full_text(query, max_price)


def mode_options(selected: str) -> str:
    modes = [
        ("fulltext", "Full-text"),
        ("vector", "Vector"),
        ("hybrid", "Hybrid"),
    ]
    return "\n".join(
        f'<option value="{value}" {"selected" if value == selected else ""}>{label}</option>'
        for value, label in modes
    )


def mode_note(mode: str) -> str:
    notes = {
        "fulltext": "Full-text search uses a DocumentDB text index and works best when query words appear in the catalog.",
        "vector": "Vector search expands broad intent such as 'mobile' or 'phone under 5000', generates an embedding, and finds phones with similar meaning.",
        "hybrid": "Hybrid search runs expanded full-text and vector search, then merges results using reciprocal rank fusion.",
    }
    return f'<div class="mode-note">{notes.get(mode, notes["fulltext"])}</div>'


def suggestion_links(selected_mode: str) -> str:
    groups = []
    for group, prompts in SUGGESTIONS.items():
        links = []
        for prompt in prompts:
            url = f"/?q={quote_plus(prompt)}&mode={selected_mode}"
            links.append(f'<a class="chip" href="{url}">{html.escape(prompt)}</a>')
        groups.append(
            f'<div class="suggestion-group"><strong>{html.escape(group)}</strong>{"".join(links)}</div>'
        )
    return f'<div class="suggestions"><p class="hint">Try these searches:</p>{"".join(groups)}</div>'


def format_score(result: dict, mode: str) -> str:
    if mode == "fallback":
        return f"Vector fallback score: {result.get('vectorScore', 0):.4f}"
    if mode == "hybrid":
        text_rank = result.get("textRank", "-")
        vector_rank = result.get("vectorRank", "-")
        return (
            f"Hybrid score: {result.get('hybridScore', 0):.4f}<br>"
            f"Text rank: {text_rank} · Vector rank: {vector_rank}"
        )
    if mode == "vector":
        expanded_query = result.get("expandedQuery")
        expanded_note = "<br>Intent expansion applied" if expanded_query else ""
        return f"Vector score: {result.get('vectorScore', 0):.4f}{expanded_note}"
    return f"Text score: {result.get('textScore', 0):.2f}"


def render_card(result: dict, mode: str) -> str:
    title = html.escape(str(result.get("title", "")))
    brand = html.escape(str(result.get("brand", "")))
    segment = html.escape(str(result.get("segment", "")))
    description = html.escape(str(result.get("description", "")))
    price = result.get("priceInr", 0)
    rating = html.escape(str(result.get("rating", "N/A")))
    camera = html.escape(str(result.get("cameraMp", "N/A")))
    battery = html.escape(str(result.get("batteryMah", "N/A")))
    score = format_score(result, mode)
    return f"""
    <article class="card">
      <div class="title">{title}</div>
      <div class="meta">{brand} · {segment}</div>
      <div class="price">INR {price:,}</div>
      <div class="meta">Rating: {rating}/5 · Camera: {camera} MP · Battery: {battery} mAh</div>
      <p>{description}</p>
      <div class="score">{score}</div>
    </article>
    """


def render_results(query: str, mode: str, max_price: int | None) -> str:
    intro = mode_note(mode)
    if not query:
        return intro + suggestion_links(mode)

    fallback_message = ""
    result_mode = mode
    try:
        results = run_search(mode, query, max_price)
        if not results and mode == "fulltext":
            results = search_vector(query, max_price)
            result_mode = "fallback"
            fallback_message = (
                '<div class="mode-note">'
                "No direct full-text match was found, so the app is showing vector results instead. "
                "This is useful for broad or intent-based searches like <strong>mobile</strong>, "
                "<strong>phone for office</strong>, or <strong>travel photos</strong>."
                "</div>"
            )
    except Exception as error:
        return (
            intro
            + '<div class="error"><strong>Search failed.</strong><br>'
            + html.escape(str(error))
            + "<br><br>If this happened in Vector or Hybrid mode, check "
            + "<code>AZURE_OPENAI_ENDPOINT</code>, <code>AZURE_OPENAI_API_KEY</code>, "
            + "and <code>AZURE_OPENAI_EMBEDDING_DEPLOYMENT</code> in your <code>.env</code> file. "
            + "The app accepts endpoints with or without <code>/openai/v1</code>.</div>"
            + suggestion_links(mode)
        )

    if not results:
        return (
            intro
            + f'<div class="empty">No results found for <strong>{html.escape(query)}</strong>.</div>'
            + suggestion_links(mode)
        )

    filter_text = f" under INR {max_price:,}" if max_price is not None else ""
    cards = "".join(render_card(item, result_mode) for item in results)
    return (
        intro
        + fallback_message
        + f"<p>Showing {len(results)} {mode_label(mode)} result(s) for "
        + f"<strong>{html.escape(query)}</strong>{filter_text}.</p>"
        + f'<div class="grid">{cards}</div>'
        + suggestion_links(mode)
    )


def mode_label(mode: str) -> str:
    return {
        "fulltext": "full-text",
        "vector": "vector",
        "hybrid": "hybrid",
    }.get(mode, "full-text")


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
        max_price = infer_max_price(query)

        content = render_results(query, mode, max_price)

        page = (
            PAGE.replace("__QUERY__", html.escape(query))
            .replace("__MODE_OPTIONS__", mode_options(mode))
            .replace("__CONTENT__", content)
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
    port = 5000
    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print("DocumentDB Mobile Search Playground is running.")
    print(f"Open: {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
