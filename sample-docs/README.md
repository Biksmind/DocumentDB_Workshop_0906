# Sample Documents

This folder contains sample documents for the three Azure DocumentDB workshop collections. Import these **after** creating the `Workshop_DB` database and its collections.

## Files

| File | Collection | Documents |
|---|---|---|
| `mobiles_sample.json` | `mobiles` | 30 mobile phones across Budget, Mid Range, Premium, Foldable, and Gaming segments |
| `support_articles_sample.json` | `support_articles` | 30 knowledge-base articles covering Battery, Camera, Connectivity, Bluetooth, Payments, and more |
| `retail_offers_sample.json` | `retail_offers` | 30 phones with retailer offer details |
| `headsets_sample.json` | `headsets` | 30 headsets across Over-ear, True Wireless, Gaming, and Studio categories for performance demo |

## When to import

Import these sample documents after you have:

1. Created the Azure DocumentDB cluster (Module 1).
2. Created the `Workshop_DB` database (Module 1 – Create the workshop database).
3. Confirmed the connection from VS Code or `mongosh`.

These documents let you verify that the collections accept data before running the full data load script in Module 3.

## How to import

### Option 1: mongoimport (recommended)

Replace `<CONNECTION_STRING>` with your DocumentDB connection string from `.env`.

```powershell
# mobiles
mongoimport --uri "<CONNECTION_STRING>" `
  --db Workshop_DB --collection mobiles `
  --file .\sample-docs\mobiles_sample.json `
  --jsonArray

# support articles
mongoimport --uri "<CONNECTION_STRING>" `
  --db Workshop_DB --collection support_articles `
  --file .\sample-docs\support_articles_sample.json `
  --jsonArray

# retail offers
mongoimport --uri "<CONNECTION_STRING>" `
  --db Workshop_DB --collection retail_offers `
  --file .\sample-docs\retail_offers_sample.json `
  --jsonArray
```

### Option 2: VS Code DocumentDB extension

1. In the DocumentDB panel, expand your cluster → `Workshop_DB`.
2. Right-click the target collection (e.g. `mobiles`).
3. Click **Import Documents...** or **Open Collection**.
4. Paste the contents of the matching sample file and save.

### Option 3: mongosh

```javascript
use Workshop_DB

// Copy-paste the JSON array from any sample file directly into mongosh
db.mobiles.insertMany([ /* paste mobiles_sample.json content here */ ])
db.support_articles.insertMany([ /* paste support_articles_sample.json content here */ ])
db.retail_offers.insertMany([ /* paste retail_offers_sample.json content here */ ])
```

## Verify the import

In `mongosh`:

```javascript
use Workshop_DB
db.mobiles.countDocuments()           // expect 30
db.support_articles.countDocuments()  // expect 30
db.retail_offers.countDocuments()     // expect 30
```

## Next step

The sample documents cover the complete workshop dataset. If you still want to run the Module 3 load script (to create indexes and re-load data), drop the collections first to avoid duplicates:

```javascript
use Workshop_DB
db.mobiles.drop()
db.support_articles.drop()
db.retail_offers.drop()
```

Then run:

```powershell
python .\scripts\load_workshop_data.py
```
