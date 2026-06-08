# Module 4: Put an AI agent on top of DocumentDB

**Duration:** 75 minutes

So far, you have queried DocumentDB directly. In this module, you will run a small app where the user talks to an AI agent. The agent decides which Python tool to call, and those tools query DocumentDB.

This is the part of the workshop where the search work starts to feel like an application.

## What you'll build

Two agents served through DevUI:

| Agent | Purpose | DocumentDB tools |
|---|---|---|
| `MobileAdvisor` | Recommends phones based on need, budget, camera, battery, gaming, and productivity | Vector search, budget search, product details |
| `RetailOfferFinder` | Finds retailers, prices, and availability | Offer lookup, retailer search |

## Prerequisites

- Completed Module 3.
- `mobiles` collection loaded.
- `retail_offers` collection loaded.
- `vector_index` exists on `mobiles.contentVector`.
- Python dependencies installed.

## Folder structure

```text
4-AI-Agents\
  mobile-agents\
    app.py
    mobile_tools.py
    retail_offers.json
```

## Step 1: Confirm setup

From the repository root:

```powershell
python .\scripts\validate_workshop_setup.py
```

You should see:

```text
Mobile workshop setup validation passed.
```

## Step 2: Launch DevUI

Run these commands from the repository root:

```powershell
cd .\4-AI-Agents\mobile-agents
python app.py
```

Open:

```text
http://localhost:8080
```

If the browser does not open automatically, copy the URL and paste it into your browser address bar.

## Step 3: Test the MobileAdvisor agent

In DevUI:

1. Click **MobileAdvisor**.
2. Wait for the chat window to open.
3. Paste one of these prompts.
4. Press **Enter**.

```text
Recommend a phone under 50000 for camera and battery
```

```text
I need a gaming phone with fast charging
```

```text
Suggest a premium business phone for productivity
```

```text
Tell me about Samsung Galaxy S24 Ultra
```

## Step 4: Test the RetailOfferFinder agent

In DevUI:

1. Go back to the agent list if needed.
2. Click **RetailOfferFinder**.
3. Paste one of these prompts.
4. Press **Enter**.

```text
Where can I buy OnePlus 12?
```

```text
What mobiles are available from Flipkart?
```

```text
Find offers for iPhone 15
```

## How it works

The agent flow:

```text
User request
  -> LLM decides which tool to call
  -> Tool queries Azure DocumentDB
  -> DocumentDB returns mobile catalog or offer data
  -> LLM formats the final response
```

The semantic recommendation flow:

```text
User: "gaming phone with fast charging"
  -> Azure OpenAI embedding
  -> DocumentDB DiskANN vector search on mobiles.contentVector
  -> Top matching phones
  -> Agent explains recommendations
```

## Tool map

| Tool | What it does |
|---|---|
| `recommend_mobiles(query, k)` | Generates embedding and runs vector search |
| `search_mobiles_by_budget(max_price_inr, min_rating)` | Finds phones within a budget |
| `get_mobile_details(title)` | Looks up one phone |
| `find_mobile_offers(title)` | Finds retail offers for one phone |
| `search_offers_by_retailer(retailer)` | Lists phones available from a retailer |

## Exercise

Add a new tool for battery-focused search:

```python
def search_mobiles_by_battery(min_battery_mah: int = 5000) -> str:
    db = _get_mongo_db()
    results = list(
        db.mobiles.find(
            {"batteryMah": {"$gte": min_battery_mah}},
            {"title": 1, "brand": 1, "batteryMah": 1, "priceInr": 1, "_id": 0},
        ).sort("batteryMah", -1)
    )
```

Then add it to the `MobileAdvisor` tools list in `app.py`.

## Troubleshooting

**`DOCUMENTDB_CONNECTION_STRING not set`**

- Confirm `.env` exists in the repository root.
- Confirm you launched the app from `4-AI-Agents\mobile-agents`.

**`mobiles` collection not found**

Run from the repository root:

```powershell
python .\scripts\load_workshop_data.py
```

**Vector search errors**

- Confirm the cluster is M30 or higher.
- Confirm `vector_index` exists with `db.mobiles.getIndexes()`.
- Confirm embeddings were generated with 256 dimensions.
