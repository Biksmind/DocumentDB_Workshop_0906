# Module 2.1: NoSQL Fundamentals with Mobiles

**Duration:** 60 minutes  
**Level:** Beginner  
**Goal:** Learn the basic MongoDB-compatible query patterns used throughout the workshop.

## Prerequisites

- Completed Module 1.
- `.env` configured.
- Mobile data loaded with:

```powershell
python .\scripts\load_workshop_data.py
python .\scripts\validate_workshop_setup.py
```

## Part 1: Why document databases?

Mobile product catalogs are a good document database use case because each product can have different attributes:

```json
{
  "title": "Samsung Galaxy S24 Ultra",
  "brand": "Samsung",
  "segment": "Ultra Premium",
  "priceInr": 129999,
  "cameraMp": 200,
  "batteryMah": 5000,
  "features": ["S Pen", "Galaxy AI", "200MP camera", "periscope zoom"],
  "useCases": ["productivity", "photography", "AI features", "business users"]
}
```

DocumentDB lets you store this flexible JSON structure and query nested arrays without forcing every product into a rigid table schema.

## Part 2: Connect and inspect data

Open `mongosh`:

```powershell
mongosh "<paste DOCUMENTDB_CONNECTION_STRING here>"
```

Run:

```javascript
use Workshop_DB

db.runCommand({ ping: 1 })
db.mobiles.countDocuments()
db.mobiles.findOne()
```

Expected count:

```text
30
```

## Part 3: Basic reads

Find all Samsung mobiles:

```javascript
db.mobiles.find(
  { brand: "Samsung" },
  { _id: 0, title: 1, brand: 1, segment: 1, priceInr: 1, rating: 1 }
)
```

Find premium mobiles:

```javascript
db.mobiles.find(
  { segment: { $regex: "Premium", $options: "i" } },
  { _id: 0, title: 1, brand: 1, segment: 1, priceInr: 1 }
)
```

## Part 4: Filters and operators

Mobiles under INR 50,000:

```javascript
db.mobiles.find(
  { priceInr: { $lte: 50000 } },
  { _id: 0, title: 1, brand: 1, priceInr: 1, rating: 1 }
).sort({ priceInr: 1 })
```

Mobiles with battery >= 5000 mAh and rating >= 4.3:

```javascript
db.mobiles.find(
  {
    batteryMah: { $gte: 5000 },
    rating: { $gte: 4.3 }
  },
  { _id: 0, title: 1, brand: 1, batteryMah: 1, rating: 1 }
).sort({ rating: -1 })
```

Mobiles with gaming in use cases:

```javascript
db.mobiles.find(
  { useCases: "gaming" },
  { _id: 0, title: 1, brand: 1, useCases: 1, priceInr: 1 }
)
```

## Part 5: Projection and limit

Return only fields needed by the UI:

```javascript
db.mobiles.find(
  { priceInr: { $lte: 40000 } },
  { _id: 0, title: 1, brand: 1, priceInr: 1 }
).limit(5)
```

This pattern is important for performance because it avoids returning large fields such as `contentVector`.

## Part 6: Aggregation

Average price by segment:

```javascript
db.mobiles.aggregate([
  {
    $group: {
      _id: "$segment",
      count: { $sum: 1 },
      avgPrice: { $avg: "$priceInr" },
      avgRating: { $avg: "$rating" }
    }
  },
  { $sort: { avgPrice: -1 } }
])
```

Top brands by catalog count:

```javascript
db.mobiles.aggregate([
  { $group: { _id: "$brand", count: { $sum: 1 } } },
  { $sort: { count: -1, _id: 1 } },
  { $limit: 10 }
])
```

Find use-case distribution:

```javascript
db.mobiles.aggregate([
  { $unwind: "$useCases" },
  { $group: { _id: "$useCases", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

## Part 7: Updates

Add a workshop note to one document:

```javascript
db.mobiles.updateOne(
  { title: "OnePlus 12" },
  { $set: { workshopNote: "Tested during NoSQL fundamentals lab" } }
)
```

Verify:

```javascript
db.mobiles.findOne(
  { title: "OnePlus 12" },
  { _id: 0, title: 1, workshopNote: 1 }
)
```

Remove the note so later modules are clean:

```javascript
db.mobiles.updateOne(
  { title: "OnePlus 12" },
  { $unset: { workshopNote: "" } }
)
```

## Part 8: Checkpoint

Run:

```javascript
db.mobiles.countDocuments()
db.retail_offers.countDocuments()
db.mobiles.getIndexes()
```

Expected:

- `mobiles`: 30
- `retail_offers`: 30
- Indexes include `mobile_text_index` and `vector_index`

## Next

Continue to [Module 3](../3-AI-Vector-Search/README.md) for full-text search, embeddings, and vector search.
