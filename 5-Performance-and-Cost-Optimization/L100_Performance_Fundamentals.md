# L100: Performance Fundamentals

**Duration:** 20 minutes  
**Goal:** Learn to read query plans and understand why indexes matter.

## Part 1: Baseline query

Run:

```javascript
use Workshop_DB

db.mobiles.find(
  { brand: "Samsung" },
  { _id: 0, title: 1, brand: 1, priceInr: 1 }
).explain("executionStats")
```

Look for:

- `winningPlan.stage`
- `totalDocsExamined`
- `nReturned`

If no supporting brand index exists, the query may scan more documents than needed.

## Part 2: Create an index

```javascript
db.mobiles.createIndex({ brand: 1 }, { name: "mobile_brand_index" })
```

Run the query again:

```javascript
db.mobiles.find(
  { brand: "Samsung" },
  { _id: 0, title: 1, brand: 1, priceInr: 1 }
).explain("executionStats")
```

The goal is to reduce unnecessary document scans.

## Part 3: Compound index

A common product-listing query filters by brand and sorts by price:

```javascript
db.mobiles.find(
  { brand: "Samsung" },
  { _id: 0, title: 1, brand: 1, priceInr: 1, rating: 1 }
).sort({ priceInr: 1 }).explain("executionStats")
```

Create a compound index:

```javascript
db.mobiles.createIndex(
  { brand: 1, priceInr: 1 },
  { name: "mobile_brand_price_index" }
)
```

Run the query again:

```javascript
db.mobiles.find(
  { brand: "Samsung" },
  { _id: 0, title: 1, brand: 1, priceInr: 1, rating: 1 }
).sort({ priceInr: 1 }).explain("executionStats")
```

## Part 4: Projection and limit

Avoid returning `contentVector` in normal UI queries:

```javascript
db.mobiles.find(
  { priceInr: { $lte: 50000 } },
  { _id: 0, title: 1, brand: 1, priceInr: 1, rating: 1 }
).sort({ rating: -1 }).limit(5)
```

Projection reduces network transfer and client processing.

## Key takeaway

Do not scale the cluster before checking query plans. Missing indexes and unbounded result sets are often the root cause of slow queries.
