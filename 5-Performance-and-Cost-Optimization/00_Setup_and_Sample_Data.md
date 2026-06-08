# Step 0: Setup and Sample Data

**Duration:** 5 minutes

Module 5 uses the same mobile catalog loaded earlier in the workshop. There is no separate e-commerce dataset.

## Run setup

From the repository root:

```powershell
python .\scripts\load_workshop_data.py
python .\scripts\validate_workshop_setup.py
```

## Verify in mongosh

```powershell
mongosh "<paste DOCUMENTDB_CONNECTION_STRING here>"
```

Inside `mongosh`:

```javascript
use Workshop_DB

db.mobiles.countDocuments()
db.retail_offers.countDocuments()
db.mobiles.getIndexes()
```

Expected:

- `mobiles`: 30
- `retail_offers`: 30
- `mobile_text_index`
- `vector_index`
- `mobile_brand_index`
- `mobile_price_index`

## Reset non-required indexes for experiments

If the instructor wants to demonstrate before/after query plans, drop only the supporting indexes. Keep text/vector indexes for Modules 3 and 4.

```javascript
db.mobiles.dropIndex("mobile_brand_index")
db.mobiles.dropIndex("mobile_segment_index")
db.mobiles.dropIndex("mobile_price_index")
db.mobiles.dropIndex("mobile_rating_index")
```

If an index does not exist, ignore the error and continue.

Recreate all indexes at any time:

```powershell
python .\scripts\load_workshop_data.py
```
