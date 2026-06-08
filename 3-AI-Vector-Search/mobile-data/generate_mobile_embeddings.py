"""Generate mobile product embeddings using Azure OpenAI from the root .env file.

Reads:  mobiles_input.ndjson
Writes: mobiles_with_vectors.json
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


def embedding_text(mobile: dict) -> str:
    parts = [
        mobile["title"],
        mobile["brand"],
        mobile["segment"],
        mobile["description"],
        "Features: " + ", ".join(mobile.get("features", [])),
        "Use cases: " + ", ".join(mobile.get("useCases", [])),
        "Connectivity: " + ", ".join(mobile.get("connectivity", [])),
    ]
    return " | ".join(parts)


def main() -> None:
    input_file = SCRIPT_DIR / "mobiles_input.ndjson"
    output_file = SCRIPT_DIR / "mobiles_with_vectors.json"
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "256"))

    print(f"Reading mobiles from {input_file}...")
    mobiles = []
    with input_file.open("r", encoding="utf-8") as file:
        for line in file:
            mobiles.append(json.loads(line.strip()))

    print(f"Loaded {len(mobiles)} mobiles")
    print(
        f"\nGenerating embeddings using Azure OpenAI "
        f"({os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-small')})..."
    )

    for index, mobile in enumerate(mobiles, 1):
        try:
            mobile["contentVector"] = generate_embedding(
                embedding_text(mobile), dimensions=dimensions
            )
            print(f"  [{index}/{len(mobiles)}] Generated embedding for '{mobile['title']}'")
        except Exception as error:
            print(f"  Error generating embedding for '{mobile['title']}': {error}")

    mobiles_with_vectors = [mobile for mobile in mobiles if "contentVector" in mobile]
    if not mobiles_with_vectors:
        raise RuntimeError("No embeddings were generated. Check Azure OpenAI configuration.")

    print(f"\nWriting results to {output_file}...")
    with output_file.open("w", encoding="utf-8") as file:
        json.dump(mobiles_with_vectors, file, indent=2)

    print(f"\nSuccessfully generated embeddings for {len(mobiles_with_vectors)} mobiles")
    print(f"   Vector dimensions: {len(mobiles_with_vectors[0]['contentVector'])}")
    print(f"   Output file: {output_file}")


if __name__ == "__main__":
    main()
