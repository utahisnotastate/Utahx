# Part 8: Apex Protocol (Bots and Zero-Downtime Deploys)

**Audience:** Security engineers, SRE, platform leads  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
**Modules:** `utahx_apex.py`, `utahx_apex_core.py`

---

## Two catastrophes Utahx eliminates

| 3 AM incident | Legacy behavior | Apex behavior |
|---------------|-----------------|---------------|
| **Bot swarm / scraper** | IP blocklists; bots rotate IPs | **Turing Tollbooth** — crypto challenge; browsers pass, `curl`/scripts fail |
| **Backend restart** | Instant **502 Bad Gateway** | **Cryogenic Stasis** — hold client up to **15s**, exponential backoff retry |

Works with **Aegis** (Slowloris, connection caps, graceful SIGTERM drain).

---

## Turing Tollbooth

- No IP blacklist maintenance  
- Time-windowed SHA-256 challenge per client  
- HTTP: `TollboothMiddleware` returns `401` + auto-verify script for bots  
- Blocks `python-requests`, `curl`, `scrapy`, and similar User-Agents  
- Valid browsers pass via User-Agent or `X-Utahx-Verify` / cookie `utahx_verify`  
- Endpoints: `/__utahx/apex/challenge`, `/__utahx/apex/challenge.js`

---

## Cryogenic TCP Stasis

When backend returns `ConnectionRefused`:

1. Utahx does **not** drop the client immediately  
2. Retries with exponential backoff (`0.5s × attempt`, cap 3s)  
3. Up to **15 seconds** total (`stasis_timeout`)  
4. HTTP reverse proxy uses the same loop via `http_request_with_stasis`  
5. User sees slightly longer load — not a hard 502  

---

## Usage

### HTTP (default with `utahx start`)

```bash
utahx start --proxy 5000 --domain example.com
```

Apex is enabled on `UtahxServer` by default (`enable_apex=True`).

### TCP Apex + Aegis

```bash
python utahx_apex_core.py
# or
python utahx_core.py   # apex=True by default on start_utahx
```

### Disable Apex (HTTP)

```python
UtahxServer(directory=".", enable_apex=False)
```

---

## Stack diagram

```
Client
  → TollboothMiddleware (HTTP bots)
  → Fluid + Cache + Prefetch + Introspection
  → Backend (with CryogenicStasis on connect failure)
```

TCP path:

```
Client
  → ApexFluidRouter (TCP UA peek + stasis connect)
  → Aegis timeouts + connection cap + graceful drain
  → Fluid viscosity
```

---

## Tests

```bash
python -m unittest test_utahx_stasis test_utahx_aegis -v
```

---

## Build standalone binary

```bash
python scripts/build_utahx_binary.py
```

---

## Related

- [Part 7 — Aegis](07-AEGIS-PROTOCOL.md)  
- [Part 3 — Migration](03-MIGRATION-GUIDE.md)  
- [Documentation index](README.md)
