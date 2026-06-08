"""Generate support article embeddings using Azure OpenAI from the root .env file.

Reads:  support_articles_input.ndjson
Writes: support_articles_with_vectors.json
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI


ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.template to .env in {ROOT_DIR} and fill in the workshop values."
        )
    return value


def normalize_azure_endpoint(value: str) -> str:
    value = value.rstrip("/")
    if value.endswith("/openai/v1"):
        value = value[: -len("/openai/v1")]
    return value


client = AzureOpenAI(
    azure_endpoint=normalize_azure_endpoint(require_env("AZURE_OPENAI_ENDPOINT")),
    api_key=require_env("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
)


def generate_embedding(text: str, dimensions: int = 256) -> list[float]:
    model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    response = client.embeddings.create(model=model, input=text, dimensions=dimensions)
    return response.data[0].embedding


def article_embedding_text(article: dict) -> str:
    return " | ".join(
        [
            article["title"],
            article["product"],
            article["category"],
            article["severity"],
            article["content"],
            "Tags: " + ", ".join(article.get("tags", [])),
        ]
    )


def main() -> None:
    input_file = SCRIPT_DIR / "support_articles_input.ndjson"
    output_file = SCRIPT_DIR / "support_articles_with_vectors.json"
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "256"))

    articles = []
    with input_file.open("r", encoding="utf-8") as file:
        for line in file:
            articles.append(json.loads(line.strip()))

    print(f"Loaded {len(articles)} support articles")
    for index, article in enumerate(articles, 1):
        article["contentVector"] = generate_embedding(
            article_embedding_text(article), dimensions=dimensions
        )
        print(f"  [{index}/{len(articles)}] Embedded '{article['title']}'")

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(articles, file, indent=2)

    print(f"\nWrote {output_file}")


if __name__ == "__main__":
    main()
