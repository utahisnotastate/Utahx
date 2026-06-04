# Utahx: The SOTA Web Engine (v2.0 — Apex Release)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Zero-Config](https://img.shields.io/badge/configuration-zero-success.svg)](docs/01-CHILD-PROTOCOL.md)
[![Downtime](https://img.shields.io/badge/downtime-obsolete-brightgreen.svg)](docs/08-APEX-PROTOCOL.md)

**Nginx is obsolete.** Utahx is a zero-config, fluid-dynamic, crash-proof web server and Layer 7 reverse proxy.

Utahx treats traffic as a physical fluid, auto-senses your project layout, and defends against Slowloris, bot swarms, and backend restarts—without `nginx.conf`.

**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Level 1: Beginners (the magic box)

1. Put your site files (`index.html`, Python API, etc.) in one folder.  
2. Install Utahx: `pip install -e .` or download a release binary.  
3. Run: `utahx start --domain yourwebsite.com`  

Utahx provisions HTTPS, detects your stack, and serves the site. No config files.

[Full beginner guide](docs/01-CHILD-PROTOCOL.md)

---

## Level 2: Business owners (ROI)

| Feature | Benefit |
|---------|---------|
| **Fluid load balancer** | Viral traffic slows smoothly—no mass 502 errors |
| **Turing Tollbooth** | Scrapers and bot swarms blocked before your database |
| **Auto-TLS** | Certificates provisioned and renewed automatically |
| **Cryo-Stasis** | Deploy new backend containers without kicking active users |

[Business guide](docs/02-BUSINESS-GUIDE.md)

---

## Level 3: Enterprise DevOps (Apex + Aegis)

| Protocol | What it does |
|----------|----------------|
| **Auto-Sensing** | Python / Node / static / SPA from directory scan |
| **Cryogenic Stasis** | 15s backend retry on `ConnectionRefused`—no instant 502 |
| **Turing Tollbooth** | Challenge verification; blocks `curl` / `requests` bots |
| **Aegis** | 5s read timeouts, 1000 conn cap, 30s SIGTERM drain |
| **Semantic pre-fetch** | Predicts next click, pre-loads assets |
| **Semantic cache** | RAM API cache by request fingerprint |

[Aegis docs](docs/07-AEGIS-PROTOCOL.md) · [Apex docs](docs/08-APEX-PROTOCOL.md)

---

## Quick start

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
pip install -e .
utahx start
```

```bash
# Reverse proxy (replaces nginx.conf)
utahx start --proxy 5000 --domain api.example.com

# Static / React / Vue build
utahx start --static --domain app.example.com
```

---

## Migration: Nginx → Utahx (30 seconds)

**Old:** 18-line `nginx.conf`, certbot, `sites-enabled`, reload.  

**New:**

```bash
cd /var/www/my_api
utahx start --proxy 5000 --domain api.mycompany.com
```

[Migration guide](docs/03-MIGRATION-GUIDE.md)

---

## Docker / Kubernetes

```bash
docker build -t utahisnotastate/utahx:latest .
docker run -d -p 8080:8080 -v $(pwd)/site:/app/site -w /app/site utahisnotastate/utahx:latest
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
```

[Enterprise scaling](docs/04-ENTERPRISE-SCALING.md)

---

## Documentation (one language per folder)

| Language | Index |
|----------|-------|
| English | [docs/README.md](docs/README.md) |
| Russian | [tdocs/README.md](tdocs/README.md) |
| Chinese | [cdocs/README.md](cdocs/README.md) |
| Estonian | [edocs/README.md](edocs/README.md) |
| Finnish | [fdocs/README.md](fdocs/README.md) |

---

## Modules

| Module | Role |
|--------|------|
| `utahx_cli` | CLI entry |
| `utahx_auto` | Zero-config HTTP server |
| `utahx_core` / `utahx_core_aegis` | TCP fluid proxy |
| `utahx_apex` / `utahx_apex_core` | Tollbooth + cryo-stasis |
| `utahx_secure` | TLS + friendly errors |
| `utahx_prefetch` / `utahx_cache` | Pre-fetch + API cache |

---

## Tests

```bash
python -m unittest discover -v
```

---

## Build binary

```bash
python scripts/build_utahx_binary.py
```

---

## License

MIT — see [LICENSE](LICENSE).

*Maintained at [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx).*
