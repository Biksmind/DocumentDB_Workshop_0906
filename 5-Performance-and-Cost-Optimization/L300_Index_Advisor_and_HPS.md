# L300: Index Advisor and High Performance Storage

**Optional advanced reading**

## Index Advisor

Use Index Advisor to identify missing indexes for repeated mobile catalog queries, such as:

```javascript
db.mobiles.find({ brand: "Samsung" }).sort({ priceInr: 1 })
```

Recommended index shape:

```javascript
{ brand: 1, priceInr: 1 }
```

## High Performance Storage

Consider High Performance Storage only when the workload requires higher IOPS or throughput than standard storage provides.

For the workshop dataset, HPS is not required.

## Guidance

- Start with query plans and indexes.
- Scale compute only after query patterns are optimized.
- Use HPS for sustained high-throughput production workloads.
