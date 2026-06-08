"""Load mobile workshop data and create required indexes.

This is the copy-paste friendly setup path for attendees.

It loads:
  - 3-AI-Vector-Search/mobile-data/mobiles_with_vectors.json -> mobiles
  - 3-AI-Vector-Search/support-data/support_articles_with_vectors.json -> support_articles
  - 4-AI-Agents/mobile-agents/retail_offers.json -> retail_offers

It creates:
  - mobile_text_index on title, brand, segment, description, features, useCases
  - vector_index on contentVector
  - support_text_index on support article title, category, content, and tags
  - support_vector_index on support article contentVector
  - lookup indexes for retail_offers
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne
from pymongo.errors import OperationFailure


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.template to .env in {ROOT_DIR} and fill in the workshop values."
        )
    return value


def load_json(path: Path) -> list[dict]:
    if not path.exists():
        if "support-data" in str(path):
            raise FileNotFoundError(
                f"Required support vector file not found: {path}\n"
                "Run this first:\n"
                "  python .\\3-AI-Vector-Search\\support-data\\generate_support_embeddings.py\n"
                "Then rerun:\n"
                "  python .\\scripts\\load_workshop_data.py"
            )
        raise FileNotFoundError(
            f"Required data file not found: {path}\n"
            "If this is the vector file, run:\n"
            "  python .\\3-AI-Vector-Search\\mobile-data\\generate_mobile_embeddings.py\n"
            "  python .\\3-AI-Vector-Search\\mobile-data\\generate_query_embeddings.py"
        )
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {path}")
    return data


def upsert_by_title(collection, documents: list[dict]) -> int:
    operations = []
    for document in documents:
        title = document.get("title")
        if not title:
            raise ValueError(f"Document missing required title field: {document}")
        operations.append(ReplaceOne({"title": title}, document, upsert=True))

    if not operations:
        return 0

    result = collection.bulk_write(operations, ordered=False)
    return result.upserted_count + result.modified_count + result.matched_count


def upsert_by_article_id(collection, documents: list[dict]) -> int:
    operations = []
    for document in documents:
        article_id = document.get("articleId")
        if not article_id:
            raise ValueError(f"Document missing required articleId field: {document}")
        operations.append(ReplaceOne({"articleId": article_id}, document, upsert=True))

    if not operations:
        return 0

    result = collection.bulk_write(operations, ordered=False)
    return result.upserted_count + result.modified_count + result.matched_count


def create_vector_index(db, collection_name: str, field_name: str, index_name: str, dimensions: int) -> None:
    try:
        db.command(
            {
                "createIndexes": collection_name,
                "indexes": [
                    {
                        "name": index_name,
                        "key": {field_name: "cosmosSearch"},
                        "cosmosSearchOptions": {
                            "kind": "vector-diskann",
                            "dimensions": dimensions,
                            "similarity": "COS",
                        },
                    }
                ],
            }
        )
        print(f"Created vector index: {collection_name}.{index_name}")
    except OperationFailure as error:
        message = str(error)
        if "already exists" in message or "IndexOptionsConflict" in message:
            print(f"Vector index already exists: {collection_name}.{index_name}")
            return
        raise


def main() -> None:
    connection_string = require_env("DOCUMENTDB_CONNECTION_STRING")
    database_name = os.getenv("DOCUMENTDB_DATABASE", "Workshop_DB")
    dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "256"))

    mobiles_path = ROOT_DIR / "3-AI-Vector-Search" / "mobile-data" / "mobiles_with_vectors.json"
    support_path = ROOT_DIR / "3-AI-Vector-Search" / "support-data" / "support_articles_with_vectors.json"
    offers_path = ROOT_DIR / "4-AI-Agents" / "mobile-agents" / "retail_offers.json"

    print("Connecting to Azure DocumentDB...")
    client = MongoClient(connection_string)
    db = client[database_name]

    print(f"Loading mobiles from {mobiles_path}...")
    mobiles = load_json(mobiles_path)
    mobiles_written = upsert_by_title(db.mobiles, mobiles)
    print(f"Loaded or updated {mobiles_written} mobile documents in {database_name}.mobiles")

    print("Creating full-text index on mobiles...")
    db.mobiles.create_index(
        [
            ("title", "text"),
            ("brand", "text"),
            ("segment", "text"),
            ("description", "text"),
            ("features", "text"),
            ("useCases", "text"),
        ],
        name="mobile_text_index",
    )
    print("Created text index: mobiles.mobile_text_index")

    print("Creating supporting filter indexes on mobiles...")
    db.mobiles.create_index("brand", name="mobile_brand_index")
    db.mobiles.create_index("segment", name="mobile_segment_index")
    db.mobiles.create_index("priceInr", name="mobile_price_index")
    db.mobiles.create_index("rating", name="mobile_rating_index")

    print("Creating DiskANN vector index on mobiles.contentVector...")
    create_vector_index(db, "mobiles", "contentVector", "vector_index", dimensions)

    print(f"Loading support articles from {support_path}...")
    support_articles = load_json(support_path)
    support_written = upsert_by_article_id(db.support_articles, support_articles)
    print(
        f"Loaded or updated {support_written} support articles "
        f"in {database_name}.support_articles"
    )

    print("Creating full-text index on support_articles...")
    db.support_articles.create_index(
        [
            ("title", "text"),
            ("product", "text"),
            ("category", "text"),
            ("content", "text"),
            ("tags", "text"),
        ],
        name="support_text_index",
    )
    print("Created text index: support_articles.support_text_index")

    print("Creating support article filter indexes...")
    db.support_articles.create_index("articleId", name="support_article_id_index", unique=True)
    db.support_articles.create_index("category", name="support_category_index")
    db.support_articles.create_index("product", name="support_product_index")
    db.support_articles.create_index("severity", name="support_severity_index")

    print("Creating DiskANN vector index on support_articles.contentVector...")
    create_vector_index(
        db,
        "support_articles",
        "contentVector",
        "support_vector_index",
        dimensions,
    )

    print(f"Loading retail offers from {offers_path}...")
    offers = load_json(offers_path)
    offers_written = upsert_by_title(db.retail_offers, offers)
    print(f"Loaded or updated {offers_written} offer documents in {database_name}.retail_offers")

    print("Creating retail offer lookup indexes...")
    db.retail_offers.create_index("title", name="offer_title_index", unique=True)
    db.retail_offers.create_index("offers.retailer", name="offer_retailer_index")
    db.retail_offers.create_index("offers.availability", name="offer_availability_index")
    print("Created retail offer lookup indexes")

    print("\nVerification:")
    print(f"  Database: {database_name}")
    print(f"  mobiles count: {db.mobiles.count_documents({})}")
    print(f"  support_articles count: {db.support_articles.count_documents({})}")
    print(f"  retail_offers count: {db.retail_offers.count_documents({})}")
    print("  mobile indexes:")
    for index in db.mobiles.list_indexes():
        print(f"    - {index['name']}")

    client.close()
    print("\nMobile workshop data load complete.")


if __name__ == "__main__":
    main()
