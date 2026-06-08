# L200: Performance and Cost Optimization

**Duration:** 15 minutes  
**Goal:** Apply production-minded tuning to the mobile catalog workload.

## ESR rule

For compound indexes, use:

```text
Equality -> Sort -> Range
```

Example query:

```javascript
db.mobiles.find(
  {
    brand: "Samsung",
    priceInr: { $lte: 100000 }
  },
  { _id: 0, title: 1, brand: 1, priceInr: 1, rating: 1 }
).sort({ rating: -1 })
```

Recommended index:

```javascript
db.mobiles.createIndex(
  { brand: 1, rating: -1, priceInr: 1 },
  { name: "mobile_brand_rating_price_index" }
)
```

## Aggregation optimization

Place `$match` early:

```javascript
db.mobiles.aggregate([
  { $match: { priceInr: { $lte: 50000 } } },
  {
    $group: {
      _id: "$brand",
      count: { $sum: 1 },
      avgPrice: { $avg: "$priceInr" },
      avgRating: { $avg: "$rating" }
    }
  },
  { $sort: { avgRating: -1 } }
])
```

## Cost controls

- Use projections so regular queries do not return `contentVector`.
- Use `limit()` for search result pages.
- Keep only indexes that support real query patterns.
- Use M30+ for DiskANN vector search, but do not over-scale before reviewing query plans.
- Enable HA for production, not for short-lived workshop clusters.

## Connection reuse

Applications should reuse one `MongoClient` per process. The Module 4 agent tools follow this pattern.
