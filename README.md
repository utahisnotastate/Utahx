# Utahx (Utah-X) v1.3

State-of-the-art web server: fluid load balancing, zero-config routing, autonomous TLS, friendly error pages, semantic pre-fetching, semantic API caching, **Aegis edge hardening**, and Docker/Kubernetes scaling.

**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Documentation

Documentation is split by language in **separate folders** (one language per page).

| Language | Index |
|----------|-------|
| **English** | [docs/README.md](docs/README.md) |
| **Russian** | [tdocs/README.md](tdocs/README.md) |
| **Chinese (Simplified)** | [cdocs/README.md](cdocs/README.md) |
| **Estonian** | [edocs/README.md](edocs/README.md) |
| **Finnish** | [fdocs/README.md](fdocs/README.md) |

| Audience (English) | Guide |
|--------------------|-------|
| Beginners | [docs/01-CHILD-PROTOCOL.md](docs/01-CHILD-PROTOCOL.md) |
| Business owners | [docs/02-BUSINESS-GUIDE.md](docs/02-BUSINESS-GUIDE.md) |
| Engineers | [docs/03-MIGRATION-GUIDE.md](docs/03-MIGRATION-GUIDE.md) |
| Enterprise / K8s | [docs/04-ENTERPRISE-SCALING.md](docs/04-ENTERPRISE-SCALING.md) |
| API gateway | [docs/05-API-GATEWAY.md](docs/05-API-GATEWAY.md) |
| Monetization | [docs/06-MONETIZATION.md](docs/06-MONETIZATION.md) |
| Aegis / security | [docs/07-AEGIS-PROTOCOL.md](docs/07-AEGIS-PROTOCOL.md) |

---

## Quick start

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
pip install -e .
utahx start
```

With a domain:

```bash
utahx start --domain utahisnotastate.com --email you@example.com
```

### Common commands

```bash
# Reverse proxy (replaces nginx.conf)
utahx start --proxy 5000 --domain utahisnotastate.com

# Static / SPA build folder
utahx start --static --domain utahisnotastate.com
```

---

## Features at a glance

| Feature | Module |
|---------|--------|
| Fluid traffic smoothing | `utahx_core`, `fluid_dynamics` |
| Zero-config project detection | `utahx_auto` |
| Autonomous TLS | `utahx_secure` |
| Friendly error dashboards | `utahx_secure` |
| Semantic pre-fetching | `utahx_prefetch` |
| Semantic API cache | `utahx_cache` |
| CLI entry point | `utahx_cli` |
| Aegis TCP hardening | `utahx_core_aegis` |

---

## Windows

Double-click `utahx.cmd` (interactive domain prompt), or build an executable:

```powershell
.\scripts\build_utahx_exe.ps1
```

---

## Docker and Kubernetes

```bash
docker build -t utahisnotastate/utahx:latest .
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
```

See [docs/04-ENTERPRISE-SCALING.md](docs/04-ENTERPRISE-SCALING.md).

---

## Tests

```bash
python -m unittest discover -v
```

---

## License

MIT — see [LICENSE](LICENSE).
