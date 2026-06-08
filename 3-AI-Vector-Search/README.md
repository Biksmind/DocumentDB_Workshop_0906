# Module 3: Search the mobile catalog

**Duration:** 60 minutes

In this module, you will move from normal database queries to search. First you will generate embeddings for each phone. Then you will load the data into Azure DocumentDB and compare keyword search with vector search.

Do not worry if the vectors look unreadable. They are supposed to look like long lists of numbers. What matters is that every mobile document gets a `contentVector` field.

## Before you start

You should already have:

- `.env` saved in the repository root.
- A working Azure DocumentDB connection string.
- A working Azure OpenAI embedding deployment.
- Python dependencies installed.

## Dataset

This module uses a mobile catalog with 30 products across Apple, Samsung, Google, OnePlus, Xiaomi, Nothing, Vivo, Oppo, Realme, Motorola, Asus, iQOO, and Poco.

Each document includes:

```json
{
  "title": "OnePlus 12",
  "brand": "OnePlus",
  "segment": "Flagship Value",
  "description": "Performance-focused Android flagship...",
  "priceInr": 64999,
  "rating": 4.6,
  "cameraMp": 50,
  "batteryMah": 5400,
  "features": ["fast charging", "Hasselblad camera"],
  "useCases": ["gaming", "performance", "battery life"],
  "contentVector": [0.012, -0.033, 0.087]
}
```

## Files

```text
3-AI-Vector-Search\mobile-data\
  mobiles_input.ndjson
  generate_mobile_embeddings.py
  generate_query_embeddings.py
  mobiles_with_vectors.json
  query_embeddings.json
```

`mobiles_with_vectors.json` and `query_embeddings.json` are generated during the workshop.

## Step 1: Generate embeddings

Open PowerShell from the repository root. If you are not sure where you are, run `Get-ChildItem` and confirm you can see `README.md`.

Run:

```powershell
python .\3-AI-Vector-Search\mobile-data\generate_mobile_embeddings.py
python .\3-AI-Vector-Search\mobile-data\generate_query_embeddings.py
```

This creates two files:

- `mobiles_with_vectors.json`
- `query_embeddings.json`

## Step 2: Load data and create indexes

Stay in the repository root and run:

```powershell
python .\scripts\load_workshop_data.py
python .\scripts\validate_workshop_setup.py
```

This loads `mobiles` and `retail_offers`, then creates text, vector, and lookup indexes. If this fails, check the firewall setting on the DocumentDB resource first.

## Step 3: Verify in mongosh

Open `mongosh` with your DocumentDB connection string. Then run:

```javascript
use Workshop_DB

db.mobiles.countDocuments()
db.retail_offers.countDocuments()
db.mobiles.getIndexes()
```

You should see:

- `mobiles`: 30 documents
- `retail_offers`: 30 documents
- Indexes include `mobile_text_index` and `vector_index`

## Step 4: Full-text search baseline

```javascript
db.mobiles.find(
  { $text: { $search: "camera phone battery 5G" } },
  {
    score: { $meta: "textScore" },
    title: 1,
    brand: 1,
    segment: 1,
    priceInr: 1,
    rating: 1,
    _id: 0
  }
).sort({ score: { $meta: "textScore" } }).limit(5)
```

This is keyword search. It is good when the user types direct words that exist in the catalog.

## Step 5: Vector search

Open this file in VS Code:

```text
3-AI-Vector-Search\mobile-data\query_embeddings.json
```

Find this query and copy its full `embedding` array:

```text
best camera phone for portraits and low light photography
```

Paste that array into `queryVector`, then run:

```javascript
const queryVector = [/* paste embedding array here */]

db.mobiles.aggregate([
  {
    $search: {
      cosmosSearch: {
        vector: queryVector,
        path: "contentVector",
        k: 5
      }
    }
  },
  {
    $project: {
      title: 1,
      brand: 1,
      segment: 1,
      priceInr: 1,
      rating: 1,
      cameraMp: 1,
      batteryMah: 1,
      score: { $meta: "searchScore" },
      _id: 0
    }
  }
])
```

This is vector search. It is useful when the user describes intent, such as:

- "phone for travel photography"
- "gaming phone with fast charging"
- "budget 5G phone for student"
- "business phone for productivity"

## Step 6: Filtered vector search

Now add a business constraint. The query still searches by meaning, but only returns phones under INR 50,000.

```javascript
db.mobiles.aggregate([
  {
    $search: {
      cosmosSearch: {
        vector: queryVector,
        path: "contentVector",
        k: 10,
        filter: {
          priceInr: { $lte: 50000 }
        }
      }
    }
  },
  {
    $project: {
      title: 1,
      brand: 1,
      priceInr: 1,
      rating: 1,
      score: { $meta: "searchScore" },
      _id: 0
    }
  }
])
```

## Search capability comparison

| Search type | Best for | Mobile example |
|---|---|---|
| Basic query | Exact filters | `brand = "Samsung"` |
| Full-text search | Keywords | `"camera battery 5G"` |
| Vector search | Intent and similarity | `"phone for portraits and low light"` |
| Filtered vector search | Intent plus business rules | Camera phone under INR 50,000 |
| Azure AI Search | Dedicated enterprise search across multiple sources | Product catalog + reviews + manuals |

## Practice exercises

1. Find a budget 5G phone for students.
2. Find a gaming phone with fast charging.
3. Find premium productivity phones.
4. Compare full-text search vs vector search for "camera phone".
5. Add a price filter to a vector query.

## Troubleshooting

**Vector index creation fails**

- Confirm the cluster is M30 or higher.
- Confirm `EMBEDDING_DIMENSIONS=256`.
- Confirm every mobile document has `contentVector`.

**Search results look unrelated**

- Regenerate both mobile and query embeddings with the same embedding deployment.
- Confirm the vector index dimension matches the generated vector dimension.

**Data load fails because `mobiles_with_vectors.json` is missing**

Run:

```powershell
python .\3-AI-Vector-Search\mobile-data\generate_mobile_embeddings.py
python .\3-AI-Vector-Search\mobile-data\generate_query_embeddings.py
```
