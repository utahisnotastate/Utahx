# Utahx Official Documentation — Part 5: Advanced API Gateway

**Audience:** Backend engineers, API owners  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Semantic Cache Layer

Nginx caches by exact URL. Utahx hashes **path + request body intent** (SHA-256 fingerprint) and serves identical API calls from RAM.

| Component | Module | Role |
|-----------|--------|------|
| `SemanticMemoryCore` | `utahx_cache.py` | Vault: fingerprint → (bytes, expiry) |
| `SemanticCacheMiddleware` | `utahx_cache.py` | Gateway middleware on GET/HEAD `/api/*` |

### Behavior

- **HIT** — instant JSON from RAM, header `X-Utahx-Cache: HIT`
- **MISS** — proxy to backend, memorize 200 responses, header `X-Utahx-Cache: MISS`
- **TTL** — default 60s (configurable on `UtahxServer`)

### Example

```python
from utahx_auto import UtahxServer

server = UtahxServer(directory=".", cache_ttl_seconds=120)
server.start(port=8080)
```

### Disable cache

```python
UtahxServer(directory=".", enable_semantic_cache=False)
```

---

## Full gateway stack (v1.2)

```
Request
  → HumanIntrospectionMiddleware
  → FluidTrafficMiddleware
  → SemanticCacheMiddleware
  → PrefetchInjectMiddleware
  → Backend / static / proxy
```

Registry: [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)
