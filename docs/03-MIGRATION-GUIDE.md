# Utahx Official Documentation — Part 3: Technical Migration Guide

**Audience:** DevOps, SRE, backend engineers  
**Registry:** [github.com/utahisnotastate/utahx](https://github.com/utahisnotastate/utahx)

Migrating from Nginx to Utahx takes **less than 60 seconds**. Utahx is a drop-in replacement that eliminates `.conf` files.

---

## Install

```bash
pip install git+https://github.com/utahisnotastate/utahx.git
# or
pip install -e .
```

---

## Scenario A: Reverse Proxy (Node.js, Python, Go)

### The old Nginx way

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

Then: `sites-available`, symlinks, `nginx -t`, reload.

### The Utahx way

```bash
cd /path/to/your/app
utahx start --proxy 5000 --domain utahisnotastate.com
```

| Behavior | Detail |
|----------|--------|
| Ports | Binds **80** / **443** (falls back to **8080** / **8443** without root) |
| TLS | Let's Encrypt via ACME v2 (`pip install utahx[secure]`) |
| Proxy | All traffic → `127.0.0.1:5000` |
| Protection | Fluid Traffic Manager on the edge |
| Pre-fetch | HTML responses inject semantic pre-fetch client |

---

## Scenario B: Static Site / SPA (React, Vue, HTML)

### The old Nginx way

- `root` / `try_files` / cache headers  
- Manual SPA fallback: `try_files $uri /index.html`

### The Utahx way

```bash
cd ./dist   # or build folder
utahx start --static --domain utahisnotastate.com
```

| Behavior | Detail |
|----------|--------|
| Auto-sense | Forces static mode |
| SPA routing | Unknown paths → `index.html` when SPA markers detected |
| Pre-fetch | `/__utahx/prefetch/*` API + injected `utahx.js` |
| MIME | FastAPI `StaticFiles` / `FileResponse` |

---

## Scenario C: Zero-Config (Magic Butler)

```bash
cd /path/to/project
utahx start
```

Utahx scans for `package.json`, `requirements.txt`, `main.py`, or `index.html` and configures routes automatically.

---

## Semantic Pre-Fetching (Technical)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/__utahx/prefetch/manifest?path=/` | GET | Link graph for current page |
| `/__utahx/prefetch/signal` | POST | Pointer telemetry → ranked prefetch URLs |
| `/__utahx/prefetch/utahx.js` | GET | Client bootstrap (injected into HTML) |

**Client behavior:** `mousemove` + hover tracking → periodic `signal` → `<link rel=prefetch>` + low-priority `fetch`.

**Server model:** `SemanticPrefetchEngine` scores links by proximity, velocity alignment, and hover state.

---

## Architecture Map

```
Internet → Utahx (443/80)
            ├── FluidTrafficMiddleware (viscosity)
            ├── HumanIntrospectionMiddleware (friendly errors)
            ├── PrefetchInjectMiddleware (HTML injection)
            ├── AutoTLSEngine (ACME / vault)
            └── Backend: static | proxy:PORT | auto-detected app
```

---

## Windows Double-Click

Place `utahx.cmd` or built `utahx.exe` in your project folder. Interactive domain prompt runs when no CLI args are passed.

Build executable:

```powershell
.\scripts\build_utahx_exe.ps1
```

---

## Enterprise & monetization

- [Docker / Kubernetes scaling](04-ENTERPRISE-SCALING.md)  
- [Semantic API cache gateway](05-API-GATEWAY.md)  
- [Utahx Cloud monetization](06-MONETIZATION.md)  

---

## Quick Reference

| Command | Use case |
|---------|----------|
| `utahx start` | Auto-sense project |
| `utahx start --static --domain example.com` | SPA / static dist |
| `utahx start --proxy 5000 --domain example.com` | Existing app on port 5000 |
| `utahx start --domain example.com --email ops@example.com` | TLS + ACME account |

Registry: [https://github.com/utahisnotastate/utahx](https://github.com/utahisnotastate/utahx)
