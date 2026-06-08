"""DocumentDB function tools for the mobile shopping AI agents."""

import os
import re
from typing import Annotated

from agent_framework import tool
from openai import AzureOpenAI
from pydantic import Field
from pymongo import MongoClient


_mongo_client = None
_openai_client = None


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


def _get_mongo_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(os.environ["DOCUMENTDB_CONNECTION_STRING"])
    db_name = os.environ.get("DOCUMENTDB_DATABASE", "Workshop_DB")
    return _mongo_client[db_name]


def _normalize_azure_endpoint(value: str) -> str:
    value = value.rstrip("/")
    if value.endswith("/openai/v1"):
        value = value[: -len("/openai/v1")]
    return value


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = AzureOpenAI(
            azure_endpoint=_normalize_azure_endpoint(os.environ["AZURE_OPENAI_ENDPOINT"]),
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        )
    return _openai_client


def _generate_embedding(text: str) -> list[float]:
    client = _get_openai_client()
    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    dimensions = int(os.environ.get("EMBEDDING_DIMENSIONS", "256"))
    response = client.embeddings.create(model=deployment, input=text, dimensions=dimensions)
    return response.data[0].embedding


def _detect_semantic_intents(query: str) -> set[str]:
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


def _expand_semantic_query(query: str) -> str:
    phrases: list[str] = []
    for intent in sorted(_detect_semantic_intents(query)):
        phrases.extend(SEMANTIC_INTENT_EXPANSIONS[intent])

    if not phrases:
        return query

    return " | ".join([query, *phrases])


def _infer_max_price(query: str) -> int | None:
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


def _format_mobile(mobile: dict, include_score: bool = False) -> str:
    price = mobile.get("priceInr", 0)
    score = mobile.get("score", 0)
    score_text = f"\n   Similarity score: {score:.4f}" if include_score else ""
    features = ", ".join(mobile.get("features", [])[:4])
    return (
        f"**{mobile['title']}** - {mobile['brand']} | {mobile['segment']}\n"
        f"   Price: INR {price:,} | Rating: {mobile.get('rating', 'N/A')}/5 | "
        f"Battery: {mobile.get('batteryMah', 'N/A')} mAh | Camera: {mobile.get('cameraMp', 'N/A')} MP\n"
        f"   Features: {features}\n"
        f"   {mobile['description']}{score_text}"
    )


@tool
def recommend_mobiles(
    query: Annotated[
        str,
        Field(
            description=(
                "Natural language description of what the customer wants, "
                "for example 'best camera phone under 50000' or 'gaming phone with long battery'"
            )
        ),
    ],
    k: Annotated[int, Field(description="Number of results to return (1-10)", ge=1, le=10)] = 5,
) -> str:
    """Recommend mobiles using semantic vector search on Azure DocumentDB."""
    expanded_query = _expand_semantic_query(query)
    query_vector = _generate_embedding(expanded_query)
    max_price = _infer_max_price(query)
    cosmos_search = {
        "vector": query_vector,
        "path": "contentVector",
        "k": k,
    }
    if max_price is not None:
        cosmos_search["filter"] = {"priceInr": {"$lte": max_price}}

    db = _get_mongo_db()
    results = list(
        db.mobiles.aggregate(
            [
                {
                    "$search": {
                        "cosmosSearch": cosmos_search
                    }
                },
                {
                    "$project": {
                        "title": 1,
                        "brand": 1,
                        "segment": 1,
                        "description": 1,
                        "priceInr": 1,
                        "rating": 1,
                        "cameraMp": 1,
                        "batteryMah": 1,
                        "features": 1,
                        "score": {"$meta": "searchScore"},
                        "_id": 0,
                    }
                },
            ]
        )
    )

    if not results:
        return "No mobile recommendations found for that request."

    budget_text = f" under INR {max_price:,}" if max_price is not None else ""
    lines = [f"Found {len(results)} matching mobiles{budget_text}:\n"]
    for index, mobile in enumerate(results, 1):
        lines.append(f"{index}. {_format_mobile(mobile, include_score=True)}\n")
    return "\n".join(lines)


@tool
def search_mobiles_by_budget(
    max_price_inr: Annotated[int, Field(description="Maximum customer budget in INR")],
    min_rating: Annotated[float, Field(description="Minimum rating from 1 to 5")] = 4.0,
) -> str:
    """Find mobiles within a budget, sorted by rating."""
    db = _get_mongo_db()
    results = list(
        db.mobiles.find(
            {"priceInr": {"$lte": max_price_inr}, "rating": {"$gte": min_rating}},
            {
                "title": 1,
                "brand": 1,
                "segment": 1,
                "description": 1,
                "priceInr": 1,
                "rating": 1,
                "cameraMp": 1,
                "batteryMah": 1,
                "features": 1,
                "_id": 0,
            },
        )
        .sort([("rating", -1), ("priceInr", 1)])
        .limit(10)
    )

    if not results:
        return f"No mobiles found under INR {max_price_inr:,} with rating >= {min_rating}."

    lines = [f"Mobiles under INR {max_price_inr:,} with rating >= {min_rating}:\n"]
    for index, mobile in enumerate(results, 1):
        lines.append(f"{index}. {_format_mobile(mobile)}\n")
    return "\n".join(lines)


@tool
def get_mobile_details(
    title: Annotated[str, Field(description="Mobile title to look up")],
) -> str:
    """Get detailed specifications for a specific mobile."""
    db = _get_mongo_db()
    mobile = db.mobiles.find_one(
        {"title": {"$regex": title, "$options": "i"}},
        {"contentVector": 0, "_id": 0},
    )
    if not mobile:
        return f"Mobile '{title}' was not found. Try a different title or ask for recommendations."

    connectivity = ", ".join(mobile.get("connectivity", []))
    features = ", ".join(mobile.get("features", []))
    use_cases = ", ".join(mobile.get("useCases", []))
    return (
        f"**{mobile['title']}**\n"
        f"Brand: {mobile['brand']}\n"
        f"Segment: {mobile['segment']}\n"
        f"Price: INR {mobile['priceInr']:,}\n"
        f"Rating: {mobile['rating']}/5\n"
        f"Camera: {mobile['cameraMp']} MP | Battery: {mobile['batteryMah']} mAh | "
        f"RAM: {mobile['ramGb']} GB | Storage: {mobile['storageGb']} GB\n"
        f"Connectivity: {connectivity}\n"
        f"Features: {features}\n"
        f"Best for: {use_cases}\n"
        f"Description: {mobile['description']}"
    )


@tool
def find_mobile_offers(
    title: Annotated[str, Field(description="Mobile title to find retail offers for")],
) -> str:
    """Find retailers, prices, and availability for a mobile."""
    db = _get_mongo_db()
    result = db.retail_offers.find_one(
        {"title": {"$regex": title, "$options": "i"}},
        {"_id": 0},
    )
    if not result:
        return f"No retail offers found for '{title}'."

    lines = [f"Retail offers for **{result['title']}**:\n"]
    for offer in result.get("offers", []):
        lines.append(
            f"- **{offer['retailer']}** ({offer['type']}) - "
            f"INR {offer['priceInr']:,}, {offer['availability']}. {offer['notes']}"
        )
    return "\n".join(lines)


@tool
def search_offers_by_retailer(
    retailer: Annotated[str, Field(description="Retailer name, for example Amazon India or Flipkart")],
) -> str:
    """Find mobiles available from a specific retailer."""
    db = _get_mongo_db()
    results = list(
        db.retail_offers.find(
            {"offers.retailer": {"$regex": retailer, "$options": "i"}},
            {"_id": 0},
        ).sort("title", 1)
    )
    if not results:
        return f"No mobiles found for retailer '{retailer}'."

    lines = [f"Mobiles available from **{retailer}**:\n"]
    for document in results:
        for offer in document.get("offers", []):
            if retailer.lower() in offer["retailer"].lower():
                lines.append(
                    f"- **{document['title']}** - INR {offer['priceInr']:,}, "
                    f"{offer['availability']} ({offer['notes']})"
                )
    return "\n".join(lines)
