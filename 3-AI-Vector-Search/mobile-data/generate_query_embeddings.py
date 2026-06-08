"""Generate query embeddings for mobile product discovery scenarios."""

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


QUERIES = [
    {
        "query": "best camera phone for portraits and low light photography",
        "description": "Customer wants strong camera, portraits, and night photography",
        "expected_matches": ["Vivo X100 Pro", "Google Pixel 8 Pro", "Samsung Galaxy S24 Ultra"],
    },
    {
        "query": "budget 5G phone for student with long battery life",
        "description": "Customer wants affordable 5G and battery life",
        "expected_matches": ["Moto G64 5G", "Redmi 13C 5G", "OnePlus Nord CE4"],
    },
    {
        "query": "gaming phone with fast processor and high refresh display",
        "description": "Customer wants gaming performance",
        "expected_matches": ["Asus ROG Phone 8 Pro", "iQOO 12", "Poco X6 Pro"],
    },
    {
        "query": "premium business phone for productivity and multitasking",
        "description": "Customer wants productivity and enterprise-friendly features",
        "expected_matches": ["Samsung Galaxy Z Fold5", "Samsung Galaxy S24 Ultra", "iPhone 15 Pro"],
    },
    {
        "query": "stylish compact phone with clean software for daily use",
        "description": "Customer wants clean UI, style, and daily reliability",
        "expected_matches": ["Nothing Phone 2a", "Motorola Edge 50 Pro", "Google Pixel 8"],
    },
]


def main() -> None:
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "256"))
    query_embeddings = []

    print("Generating mobile query embeddings...\n")
    for query in QUERIES:
        embedding = generate_embedding(query["query"], dimensions=dimensions)
        query_embeddings.append({**query, "embedding": embedding})
        print(f"Generated: \"{query['query']}\"")

    output_file = SCRIPT_DIR / "query_embeddings.json"
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(query_embeddings, file, indent=2)

    print(f"\nSaved {len(query_embeddings)} query embeddings to {output_file}")


if __name__ == "__main__":
    main()
