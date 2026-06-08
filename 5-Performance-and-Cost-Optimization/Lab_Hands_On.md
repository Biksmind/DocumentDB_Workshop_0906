# Hands-On Lab: Mobile Catalog Performance Optimization

**Duration:** 20-30 minutes

## Lab 1: Diagnose and index brand lookup

```javascript
use Workshop_DB

db.mobiles.find(
  { brand: "Samsung" },
  { _id: 0, title: 1, brand: 1, priceInr: 1 }
).explain("executionStats")
```

Create index:

```javascript
db.mobiles.createIndex({ brand: 1 }, { name: "mobile_brand_index" })
```

Re-test:

```javascript
db.mobiles.find(
  { brand: "Samsung" },
  { _id: 0, title: 1, brand: 1, priceInr: 1 }
).explain("executionStats")
```

## Lab 2: Optimize budget search

Baseline:

```javascript
db.mobiles.find(
  { priceInr: { $lte: 50000 } },
  { _id: 0, title: 1, brand: 1, priceInr: 1, rating: 1 }
).sort({ rating: -1 }).explain("executionStats")
```

Create index:

```javascript
db.mobiles.createIndex(
  { rating: -1, priceInr: 1 },
  { name: "mobile_rating_price_index" }
)
```

Re-test:

```javascript
db.mobiles.find(
  { priceInr: { $lte: 50000 } },
  { _id: 0, title: 1, brand: 1, priceInr: 1, rating: 1 }
).sort({ rating: -1 }).limit(5).explain("executionStats")
```

## Lab 3: Explain text and vector indexes

Text search:

```javascript
db.mobiles.find(
  { $text: { $search: "camera battery 5G" } },
  { _id: 0, title: 1, brand: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } }).limit(5)
```

Vector index check:

```javascript
db.mobiles.getIndexes()
```

Confirm `vector_index` exists on `contentVector`.

## Lab 4: Production checklist

Discuss:

- Which queries need indexes?
- Which indexes are only useful for the workshop?
- Which queries should use projections?
- Which workloads require M30+?
- Would this workload need HA in production?
