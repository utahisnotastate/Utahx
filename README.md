# Utahx (Utah-X) v1.2

SOTA web server: fluid load balancing, zero-config routing, auto-TLS, friendly errors, semantic pre-fetching, **semantic API cache**, and **Docker/Kubernetes** scaling.

**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

## Documentation

| Audience | Guide |
|----------|-------|
| Beginners | [docs/01-CHILD-PROTOCOL.md](docs/01-CHILD-PROTOCOL.md) |
| Business owners | [docs/02-BUSINESS-GUIDE.md](docs/02-BUSINESS-GUIDE.md) |
| Engineers | [docs/03-MIGRATION-GUIDE.md](docs/03-MIGRATION-GUIDE.md) |
| Enterprise | [docs/04-ENTERPRISE-SCALING.md](docs/04-ENTERPRISE-SCALING.md) |
| API gateway | [docs/05-API-GATEWAY.md](docs/05-API-GATEWAY.md) |
| Monetization | [docs/06-MONETIZATION.md](docs/06-MONETIZATION.md) |

## Quick start

```bash
pip install -e .
utahx start --domain utahisnotastate.com
```

```bash
# Reverse proxy (replaces nginx.conf)
utahx start --proxy 5000 --domain utahisnotastate.com

# Static / SPA dist
utahx start --static --domain utahisnotastate.com
```

## Semantic pre-fetching

Utahx injects a predictive client into HTML pages. It tracks pointer movement and page context, then pre-streams likely next pages before the click.

## Windows

Double-click `utahx.cmd` or build `utahx.exe`:

```powershell
.\scripts\build_utahx_exe.ps1
```

## Docker & Kubernetes

```bash
docker build -t utahisnotastate/utahx:latest .
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
```

## Tests

```powershell
py -3.11 -m unittest discover -v
```
