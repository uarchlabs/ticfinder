# Why Your Cache Is Lying To You

In today's fast-paced engineering landscape, caching is everywhere. But it's
worth noting that most teams get it wrong.

Here's the thing: a stale cache isn't a performance optimization — it's a
correctness bug wearing a performance costume. The distinction matters more
than most engineers realize.

## The real problem

The issue isn't about speed, it's about trust. When you cannot verify that a
cached value reflects reality, every downstream decision inherits that
uncertainty, making the entire system harder to reason about.

Consider a typical setup. The service reads from Redis, falls back to Postgres,
and writes through on miss. This is not merely a technical choice but an
architectural commitment. The cache becomes load-bearing infrastructure.

Let me be clear about what happens next. Invalidation is the heavy lifting
nobody wants to do, and this is the true problem with most cache layers.

```python
# this em dash — should be ignored
def get(key):
    return cache.get(key) or db.fetch(key)
```

Crucially, the blast radius of a bad invalidation extends far beyond the
request that triggered it, cascading through every service that trusted the
value.

We rebuilt ours last quarter. The new design is simpler, faster, and easier to
debug. It took three weeks.

Ultimately, the lesson is not that caching is bad but that caching is a
commitment. You are promising the reader — sorry, the caller — that this value
means something.

