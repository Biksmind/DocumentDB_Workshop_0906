# Knowledge Check Exercises

## Question 1

A query filters by `brand` and sorts by `priceInr`. Which index is most useful?

```javascript
db.mobiles.createIndex({ brand: 1, priceInr: 1 })
```

## Question 2

Why should regular UI queries exclude `contentVector`?

Answer: Vectors are large and are not needed for normal list views. Excluding them reduces network transfer and client processing.

## Question 3

When should you choose M30 or higher?

Answer: Use M30 or higher when you need DiskANN vector indexing for the workshop or production vector search workloads.
