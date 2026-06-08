# L300: Sharding and Scaling

**Optional advanced reading**

## When scaling becomes relevant

The workshop dataset is intentionally small. In production, a mobile catalog platform may scale because of:

- Millions of product or SKU documents.
- Heavy read traffic from search pages.
- High write frequency from price and availability updates.
- Large vector search workloads.

## Shard key considerations

Good shard keys have high cardinality and distribute writes.

Potential candidates:

| Field | Notes |
|---|---|
| `brand` | Easy to understand, but low cardinality; not ideal alone |
| `title` | High cardinality, but not always aligned to range queries |
| synthetic product ID | Usually better for even distribution |
| retailer offer ID | Useful for high-volume offer updates |

## Scaling path

1. Optimize indexes and query shapes.
2. Use projections and limits.
3. Scale up cluster tier if CPU or memory is constrained.
4. Scale out with sharding when data and write volume require it.

## Production note

Treat shard keys as long-term design decisions. Avoid choosing a shard key that may need frequent updates.
