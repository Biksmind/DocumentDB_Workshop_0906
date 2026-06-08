"""Module 4: Mobile shopping AI agents with Azure DocumentDB."""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from agent_framework.devui import serve  # noqa: E402
from agent_framework.openai import OpenAIChatClient  # noqa: E402

from mobile_tools import (  # noqa: E402
    find_mobile_offers,
    get_mobile_details,
    recommend_mobiles,
    search_mobiles_by_budget,
    search_offers_by_retailer,
)


def normalize_azure_endpoint(value: str) -> str:
    value = value.rstrip("/")
    if value.endswith("/openai/v1"):
        value = value[: -len("/openai/v1")]
    return value


def azure_openai_base_url(value: str) -> str:
    return normalize_azure_endpoint(value) + "/openai/v1"


chat_client = OpenAIChatClient(
    model=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini"),
    base_url=azure_openai_base_url(os.environ["AZURE_OPENAI_ENDPOINT"]),
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)


mobile_advisor_agent = chat_client.as_agent(
    name="MobileAdvisor",
    instructions="""You are a mobile phone advisor powered by Azure DocumentDB.
You help users choose mobiles based on needs, budget, camera, battery, gaming,
productivity, software experience, and brand preferences.

Use recommend_mobiles when the user describes needs in natural language.
Use search_mobiles_by_budget when the user gives a budget.
Use get_mobile_details when the user asks about a specific model.

Always explain why each recommendation fits the customer's requirement.""",
    tools=[recommend_mobiles, search_mobiles_by_budget, get_mobile_details],
)


retail_offer_agent = chat_client.as_agent(
    name="RetailOfferFinder",
    instructions="""You help users find retail offers and availability for mobiles.

Use find_mobile_offers when the user asks where to buy a specific mobile.
Use search_offers_by_retailer when the user asks what is available from a retailer.

Clearly show retailer, price, availability, and notes such as exchange or EMI offers.""",
    tools=[find_mobile_offers, search_offers_by_retailer],
)


if __name__ == "__main__":
    print("=" * 60)
    print("  Module 4: Mobile Shopping AI Agents with DocumentDB")
    print("  Launching DevUI...")
    print("=" * 60)
    print()
    print("  Agents available:")
    print("    1. MobileAdvisor      - Semantic mobile recommendations")
    print("    2. RetailOfferFinder  - Retailer offers and availability")
    print()
    print("  Open http://localhost:8080 in your browser")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    serve(
        entities=[mobile_advisor_agent, retail_offer_agent],
        auto_open=True,
        port=8080,
        auth_enabled=False,
    )
