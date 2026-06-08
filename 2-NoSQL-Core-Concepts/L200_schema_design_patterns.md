# Module 2.2: Schema Design Patterns for Mobile Catalogs

**Optional extension module**

This module explains how to model mobile product catalog data in DocumentDB.

## Pattern 1: Embed bounded attributes

Use embedded arrays for bounded product attributes such as features, connectivity, and use cases:

```json
{
  "title": "OnePlus 12",
  "features": ["fast charging", "Hasselblad camera", "large battery"],
  "connectivity": ["5G", "Wi-Fi 7", "USB-C"],
  "useCases": ["gaming", "performance", "battery life"]
}
```

This is efficient because the app usually displays these fields with the product.

## Pattern 2: Separate frequently changing data

Retail prices and availability change more often than product specifications. Keep them in a separate collection:

```javascript
db.retail_offers.findOne({ title: "OnePlus 12" })
```

This avoids rewriting the main product document every time a retailer changes price.

## Pattern 3: Computed fields

Fields like `segment`, `rating`, or derived tags can help search and filtering:

```javascript
db.mobiles.createIndex({ segment: 1, priceInr: 1 })
```

## Pattern 4: Vector field colocated with source text

For the workshop, `contentVector` is stored inside the same mobile document:

```json
{
  "title": "Google Pixel 8 Pro",
  "description": "AI-first Android flagship...",
  "contentVector": [0.012, -0.034, 0.056]
}
```

This keeps retrieval simple for application developers.

## Design exercise

Add a new field for warranty information:

```javascript
db.mobiles.updateOne(
  { title: "OnePlus 12" },
  {
    $set: {
      warranty: {
        durationMonths: 12,
        provider: "Manufacturer",
        accidentalDamage: false
      }
    }
  }
)
```

Query:

```javascript
db.mobiles.find(
  { "warranty.durationMonths": { $gte: 12 } },
  { _id: 0, title: 1, warranty: 1 }
)
```

Cleanup:

```javascript
db.mobiles.updateOne(
  { title: "OnePlus 12" },
  { $unset: { warranty: "" } }
)
```
