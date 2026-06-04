# Part 5: Advanced API Gateway

**Audience:** Backend engineers and API owners  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Why Utahx adds a gateway layer

Nginx caches by **exact URL**. Two requests with the same path but different query bodies may still hit the backend twice. Utahx **semantic cache** fingerprints **path + body** so logically identical API calls return instantly from RAM.

This is an edge gateway concern: it runs before your application worker pool.

---

## Components

| Class | File | Role |
|-------|------|------|
| `SemanticMemoryCore` | `utahx_cache.py` | SHA-256 vault: fingerprint → (bytes, expiry) |
| `SemanticCacheMiddleware` | `utahx_cache.py` | HTTP middleware for cacheable requests |

---

## Cache rules

| Rule | Value |
|------|-------|
| Methods | `GET`, `HEAD` |
| Paths | `/api/*` or `Accept: application/json` |
| Skipped | `/__utahx/*` internal routes |
| Success stored | HTTP **200** responses only |
| Default TTL | **60** seconds |

---

## Response headers

| Header | Meaning |
|--------|---------|
| `X-Utahx-Cache: HIT` | Served from memory |
| `X-Utahx-Cache: MISS` | Backend executed; response memorized |

Use these in load tests and APM to measure cache effectiveness.

---

## Python configuration

```python
from utahx_auto import UtahxServer

# Longer TTL for read-heavy APIs
server = UtahxServer(
    directory=".",
    cache_ttl_seconds=300,
    enable_semantic_cache=True,
)
server.start(port=8080)
```

Disable cache:

```python
UtahxServer(directory=".", enable_semantic_cache=False)
```

---

## Direct cache API (advanced)

```python
from utahx_cache import SemanticMemoryCore

cache = SemanticMemoryCore(time_to_live_seconds=120)
cache.memorize("/api/user", b"id=1", b'{"name":"Ada"}')
assert cache.retrieve("/api/user", b"id=1") is not None
```

---

## Full edge stack (v1.2)

```
HTTP Request
    │
    ▼
HumanIntrospectionMiddleware     ← friendly errors
    │
    ▼
FluidTrafficMiddleware           ← viscosity under load
    │
    ▼
SemanticCacheMiddleware          ← RAM API cache
    │
    ▼
PrefetchInjectMiddleware         ← HTML pre-fetch (not API JSON)
    │
    ▼
Application (static / proxy / auto-started backend)
```

---

## Capacity planning

| Factor | Guidance |
|--------|----------|
| Memory | Each cached entry holds full response bytes until TTL |
| Cardinality | High-cardinality bodies reduce hit rate |
| Invalidation | TTL-only today; shorten TTL after deploys |
| Multi-pod | Per-pod cache; use Redis for shared cache at scale |

---

## Testing

```bash
python -m unittest test_utahx_cache -v
```

---

## Related

- [Part 3 — Migration](03-MIGRATION-GUIDE.md)  
- [Part 4 — Enterprise Scaling](04-ENTERPRISE-SCALING.md)
