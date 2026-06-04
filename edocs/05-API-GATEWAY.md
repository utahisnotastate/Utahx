# Osa 5: Täiustatud API lüüs

**Sihtrühm:** Backend-insenerid ja API omanikud  
**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Miks Utahx lüüs

Nginx vahendab **täpse URL-i** järgi. Utahx **semantiline vahemälu** teeb sõrmejälje **teest + kehast** — loogiliselt identsed API kõned RAM-ist.

Kiht on **servas**, enne rakenduse worker pooli.

---

## Komponendid

| Klass | Fail | Roll |
|-------|------|------|
| `SemanticMemoryCore` | `utahx_cache.py` | Vault: sõrmejälg → (bytes, aegumine) |
| `SemanticCacheMiddleware` | `utahx_cache.py` | HTTP middleware |

---

## Reeglid

| Reegel | Väärtus |
|--------|---------|
| Meetodid | `GET`, `HEAD` |
| Teed | `/api/*` või `Accept: application/json` |
| Vahele | `/__utahx/*` |
| Salvestab | HTTP **200** |
| TTL | **60** s |

---

## Päised

| Päis | Tähendus |
|------|----------|
| `X-Utahx-Cache: HIT` | Mälu |
| `X-Utahx-Cache: MISS` | Backend + salvestus |

---

## Python

```python
from utahx_auto import UtahxServer

server = UtahxServer(
    directory=".",
    cache_ttl_seconds=300,
    enable_semantic_cache=True,
)
server.start(port=8080)
```

Keela:

```python
UtahxServer(directory=".", enable_semantic_cache=False)
```

---

## Täielik serva stack (v1.2)

```
HTTP päring
    → HumanIntrospectionMiddleware
    → FluidTrafficMiddleware
    → SemanticCacheMiddleware
    → PrefetchInjectMiddleware
    → Rakendus
```

---

## Maht planeerimine

| Tegur | Juhend |
|-------|--------|
| RAM | Täielik vastus kuni TTL |
| Kardinaalsus | Rohkem kehasid → madalam HIT |
| Invalideerimine | Praegu ainult TTL |
| Mitu podi | Redis klastris |

---

## Testid

```bash
python -m unittest test_utahx_cache -v
```

---

## Seotud

- [Osa 3](03-MIGRATION-GUIDE.md)  
- [Osa 4](04-ENTERPRISE-SCALING.md)
