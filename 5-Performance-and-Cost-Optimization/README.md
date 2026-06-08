# Module 5: Performance and Cost Optimization with Mobile Catalog Data

**Duration in 7-hour workshop:** 45 minutes  
**Goal:** Learn practical query tuning, indexing, vector workload sizing, and cost controls using the same `mobiles` collection used throughout the workshop.

## Why this module matters

The sample dataset is small, so most queries will look fast. The habits still matter. In production, missing indexes and unbounded queries are usually the first things to check before scaling the cluster.

In this module, you will:

- Use `.explain("executionStats")` to identify collection scans.
- Create single-field and compound indexes.
- Use projections and limits to reduce data transfer.
- Understand text/vector index cost considerations.
- Choose scale and high availability settings for production.

## Copy-paste path

Complete these files in order:

1. [00 Setup and Sample Data](00_Setup_and_Sample_Data.md)
2. [L100 Performance Fundamentals](L100_Performance_Fundamentals.md)
3. [L200 Performance and Cost Optimization](L200_Performance_and_Cost_Optimization.md)
4. [Hands-On Lab](Lab_Hands_On.md)
5. [Exercises](Exercises.md)

Optional advanced reading:

- [L300 Index Advisor and HPS](L300_Index_Advisor_and_HPS.md)
- [L300 Sharding and Scaling](L300_Sharding_and_Scaling.md)

## Public workshop rule

This module does **not** require a separate dataset. It uses:

- `Workshop_DB.mobiles`
- `Workshop_DB.retail_offers`

These are loaded by:

```powershell
python .\scripts\load_workshop_data.py
python .\scripts\validate_workshop_setup.py
```
