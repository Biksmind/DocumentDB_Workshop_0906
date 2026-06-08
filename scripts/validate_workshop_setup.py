"""Validate that the workshop database is ready for Modules 3 and 4."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


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


def main() -> None:
    connection_string = require_env("DOCUMENTDB_CONNECTION_STRING")
    database_name = os.getenv("DOCUMENTDB_DATABASE", "Workshop_DB")

    client = MongoClient(connection_string)
    db = client[database_name]

    print(f"Validating database: {database_name}")
    print("Ping:", db.command({"ping": 1}))

    mobiles_count = db.mobiles.count_documents({})
    support_count = db.support_articles.count_documents({})
    offers_count = db.retail_offers.count_documents({})
    mobile_indexes = {index["name"] for index in db.mobiles.list_indexes()}
    support_indexes = {index["name"] for index in db.support_articles.list_indexes()}
    offer_indexes = {index["name"] for index in db.retail_offers.list_indexes()}

    checks = [
        ("mobiles collection has 30 documents", mobiles_count == 30),
        ("support_articles collection has 18 documents", support_count == 18),
        ("retail_offers collection has 30 documents", offers_count == 30),
        ("mobile_text_index exists", "mobile_text_index" in mobile_indexes),
        ("vector_index exists", "vector_index" in mobile_indexes),
        ("support_text_index exists", "support_text_index" in support_indexes),
        ("support_vector_index exists", "support_vector_index" in support_indexes),
        ("offer_title_index exists", "offer_title_index" in offer_indexes),
        ("offer_retailer_index exists", "offer_retailer_index" in offer_indexes),
    ]

    print("\nChecks:")
    failed = False
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {label}")
        failed = failed or not passed

    print("\nCounts:")
    print(f"  mobiles: {mobiles_count}")
    print(f"  support_articles: {support_count}")
    print(f"  retail_offers: {offers_count}")

    client.close()

    if failed:
        raise SystemExit("\nValidation failed. Re-run: python scripts\\load_workshop_data.py")

    print("\nWorkshop setup validation passed.")


if __name__ == "__main__":
    main()
