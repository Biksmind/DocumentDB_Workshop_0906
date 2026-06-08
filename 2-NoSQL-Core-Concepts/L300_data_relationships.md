# Module 2.3: Data Relationships for Mobile Commerce

**Optional extension module**

This module shows how relationships work in the mobile catalog scenario.

## One-to-few: embed

Embed small bounded lists directly in `mobiles`:

```javascript
db.mobiles.findOne(
  { title: "OnePlus 12" },
  { _id: 0, title: 1, features: 1, useCases: 1 }
)
```

## One-to-many: reference

Retail offers are separate because a product can have multiple offers that change frequently:

```javascript
db.retail_offers.findOne(
  { title: "OnePlus 12" },
  { _id: 0, title: 1, offers: 1 }
)
```

## Application-side join

MongoDB-compatible applications often join in application code:

```javascript
const mobile = db.mobiles.findOne(
  { title: "OnePlus 12" },
  { contentVector: 0 }
)

const offers = db.retail_offers.findOne(
  { title: "OnePlus 12" }
)

printjson({ mobile, offers })
```

## Aggregation lookup option

For reporting scenarios, you can use `$lookup`:

```javascript
db.mobiles.aggregate([
  { $match: { title: "OnePlus 12" } },
  {
    $lookup: {
      from: "retail_offers",
      localField: "title",
      foreignField: "title",
      as: "retail"
    }
  },
  { $project: { contentVector: 0 } }
])
```

## Modeling rule of thumb

| Relationship | Recommended pattern |
|---|---|
| Features, connectivity, use cases | Embed in `mobiles` |
| Retail offers and availability | Separate `retail_offers` collection |
| User reviews at large scale | Separate `reviews` collection |
| Search embeddings | Store with source document for simple retrieval |
