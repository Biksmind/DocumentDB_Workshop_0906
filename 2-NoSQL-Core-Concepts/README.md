# Module 2: NoSQL Core Concepts with Mobile Catalog Data

**Duration in 7-hour workshop:** 60 minutes  
**Goal:** Learn core document database operations using the same mobile catalog scenario used by the rest of the workshop.

## What this module covers

- Why document databases are useful for flexible product catalogs.
- How mobile product data is represented as JSON documents.
- How to insert, query, filter, sort, project, update, and aggregate documents.
- How these query patterns prepare you for full-text search, vector search, and AI agents.

## Required path for the public workshop

Complete:

1. [L100: NoSQL Fundamentals](L100_nosql_fundamentals.md)

The L200 and L300 files are optional extension material for longer deliveries:

- [L200: Schema Design Patterns](L200_schema_design_patterns.md)
- [L300: Data Relationships](L300_data_relationships.md)

## Setup check

From the repository root, make sure the mobile data has been generated and loaded:

```powershell
python .\3-AI-Vector-Search\mobile-data\generate_mobile_embeddings.py
python .\3-AI-Vector-Search\mobile-data\generate_query_embeddings.py
python .\scripts\load_workshop_data.py
python .\scripts\validate_workshop_setup.py
```

Then open `mongosh`:

```powershell
mongosh "<paste DOCUMENTDB_CONNECTION_STRING here>"
```

Inside `mongosh`:

```javascript
use Workshop_DB
db.mobiles.countDocuments()
```

Expected:

```text
30
```

## What you will use

You will explore the `mobiles` collection:

```javascript
db.mobiles.findOne()
```

Each mobile document includes brand, segment, price, rating, camera, battery, features, use cases, and a vector field used later for semantic search.

## Next module

After L100, continue to:

[Module 3: Embeddings, Full-Text Search, and Vector Search](../3-AI-Vector-Search/README.md)
