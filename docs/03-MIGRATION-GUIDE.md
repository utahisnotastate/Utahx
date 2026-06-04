# Part 3: Technical Migration Guide

**Audience:** DevOps, SRE, backend engineers  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

Utahx replaces Nginx **configuration files** with a single CLI. Most migrations complete in **under 60 seconds** after install.

---

## Install

> **Note:** Command examples use `utahx` after `pip install -e .`. You can also run `python -m utahx_cli start` with the same flags.

### From GitHub

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
pip install -e .
```

### Requirements

- Python **3.11+**
- Dependencies in `requirements.txt` (FastAPI, Uvicorn, httpx, cryptography)
- Optional ACME: `pip install -e ".[secure]"`

Verify:

```bash
python -m unittest discover -v
```

---

## Scenario A: reverse proxy (Node.js, Python, Go)

### Before: Nginx

```nginx
server {
    listen 80;
    server_name utahisnotastate.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Plus `sites-available`, symlinks, `nginx -t`, and reload.

### After: Utahx

```bash
cd /path/to/your/app
utahx start --proxy 5000 --domain utahisnotastate.com --email ops@example.com
```

| Setting | Behavior |
|---------|----------|
| Listen | **443** with TLS when `--domain` is set; **8080** locally without domain |
| Upstream | `http://127.0.0.1:5000` |
| Headers | Standard reverse proxy forwarding via httpx |
| Edge protection | FluidTrafficMiddleware |
| HTML sites | Pre-fetch script injection on HTML responses |

Your application must already listen on the target port (for example Flask on 5000).

---

## Scenario B: static site or SPA (React, Vue, HTML)

### Before: Nginx

- `root` directive  
- `try_files $uri $uri/ /index.html` for client-side routing  
- Manual cache headers  

### After: Utahx

```bash
cd ./dist
utahx start --static --domain utahisnotastate.com
```

| Setting | Behavior |
|---------|----------|
| Mode | Forces static file serving |
| SPA | Unknown paths fall back to `index.html` when SPA markers are detected |
| Pre-fetch | `/__utahx/prefetch/*` endpoints + injected client script |
| Files | Served via FastAPI `FileResponse` / `StaticFiles` |

---

## Scenario C: zero-config (magic butler)

```bash
cd /path/to/project
utahx start
```

Detection order:

1. `package.json` → Node.js (attempts `npm run start` on internal port + proxy)  
2. `requirements.txt` or `main.py` → Python (uvicorn `main:app` + proxy)  
3. `index.html` → static site  
4. Otherwise → safe static fallback  

---

## Middleware and request flow

```
Internet
    │
    ▼
Utahx listener (80 / 443 / 8080)
    │
    ├── HumanIntrospectionMiddleware   (friendly 404/502/500)
    ├── FluidTrafficMiddleware         (viscosity / Reynolds)
    ├── SemanticCacheMiddleware        (API RAM cache)
    ├── PrefetchInjectMiddleware       (HTML pre-fetch)
    ├── AutoTLSEngine                  (ACME / .utahx/vault)
    └── Route target
            ├── Static / SPA files
            ├── Reverse proxy → :PORT
            └── Auto-started Python / Node backend
```

Core modules: `utahx_cli`, `utahx_auto`, `utahx_core`, `utahx_core_aegis`, `utahx_secure`, `utahx_prefetch`, `utahx_cache`.

---

## Aegis TCP hardening (production)

Standalone TCP proxy (`utahx_core` / `utahx_core_aegis`) enables Aegis **by default**:

| Control | Default | Purpose |
|---------|---------|---------|
| `network_timeout` | 5s | Slowloris / idle client drop |
| `max_connections` | 1000 | RAM boundary |
| `drain_timeout` | 30s | Graceful SIGINT/SIGTERM drain |

Full guide: [Part 7 — Aegis Protocol](07-AEGIS-PROTOCOL.md).

---

## Semantic pre-fetching (API reference)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/__utahx/prefetch/manifest?path=/` | GET | Link graph for current page |
| `/__utahx/prefetch/signal` | POST | Pointer telemetry → ranked URLs |
| `/__utahx/prefetch/utahx.js` | GET | Browser bootstrap script |

Server module: `utahx_prefetch.SemanticPrefetchEngine`

---

## Semantic cache (API reference)

| Header | Meaning |
|--------|---------|
| `X-Utahx-Cache: HIT` | Served from RAM |
| `X-Utahx-Cache: MISS` | Fetched from backend and stored |

Default TTL: **60 seconds**. Configure with `UtahxServer(cache_ttl_seconds=120)`.

---

## TLS and certificates

```bash
utahx start --domain example.com --email admin@example.com
```

- Production ACME: install `utahx[secure]` and ensure HTTP-01 reachability on port 80  
- Development fallback: ECDSA cert in `.utahx/vault/`  
- Staging CA: add `--staging`  

---

## Windows workflow

1. Copy project files and `utahx.cmd` into one folder.  
2. Double-click `utahx.cmd` (interactive domain prompt).  
3. Or build `utahx.exe`: `.\scripts\build_utahx_exe.ps1`

---

## Environment variables

| Variable | Purpose |
|----------|---------|
| `UTAHX_STATELESS` | Set to `1` in containers (no reliance on local state) |
| `UTAHX_PORT` | Container listen port (default **8080** in Docker) |

---

## Quick reference

| Command | Use case |
|---------|----------|
| `utahx start` | Auto-detect project type |
| `utahx start --static --domain example.com` | SPA / static build output |
| `utahx start --proxy 5000 --domain example.com` | Existing app on port 5000 |
| `utahx start --domain example.com --email ops@example.com` | TLS + ACME account |
| `utahx start --port 9000` | Custom listen port |

---

## Related guides

- [Part 4 — Enterprise Scaling](04-ENTERPRISE-SCALING.md)  
- [Part 5 — API Gateway](05-API-GATEWAY.md)  
- [Part 6 — Monetization](06-MONETIZATION.md)  
- [Documentation index](README.md)
