# Utahx Documentation (English)

Official documentation for the Utahx SOTA Web Engine.

**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Documentation map

| Part | Document | Who it is for |
|------|----------|---------------|
| 1 | [01-CHILD-PROTOCOL.md](01-CHILD-PROTOCOL.md) | Beginners and non-technical users |
| 2 | [02-BUSINESS-GUIDE.md](02-BUSINESS-GUIDE.md) | Founders, product owners, operators |
| 3 | [03-MIGRATION-GUIDE.md](03-MIGRATION-GUIDE.md) | DevOps, SRE, backend engineers |
| 4 | [04-ENTERPRISE-SCALING.md](04-ENTERPRISE-SCALING.md) | Platform teams, Docker and Kubernetes |
| 5 | [05-API-GATEWAY.md](05-API-GATEWAY.md) | API owners, backend engineers |
| 6 | [06-MONETIZATION.md](06-MONETIZATION.md) | GTM, enterprise sales, founders |
| 7 | [07-AEGIS-PROTOCOL.md](07-AEGIS-PROTOCOL.md) | Security engineers, edge hardening |

---

## Recommended reading order

1. **New to servers?** Start with Part 1.  
2. **Running a business on the site?** Read Part 2, then Part 3.  
3. **Replacing Nginx?** Go straight to Part 3.  
4. **Scaling to millions of users?** Parts 4 and 5.  
5. **Building a product company around Utahx?** Part 6.  
6. **Hardening for production / hostile traffic?** Part 7 (Aegis).

---

## What Utahx replaces

Utahx is a single binary and CLI that replaces manual **Nginx configuration**, **Certbot workflows**, basic **reverse proxy** setup, and ad-hoc **rate limiting** with:

- Fluid traffic smoothing (no hard connection drops)
- Zero-config project detection
- Autonomous TLS provisioning
- Human-readable error pages
- Semantic pre-fetching for HTML sites
- Semantic API caching for JSON endpoints
- Production-ready Docker and Kubernetes manifests
- **Aegis edge hardening** (timeouts, connection caps, graceful drain)

---

## Quick links

- [Install and first run](03-MIGRATION-GUIDE.md#install)
- [Docker and Kubernetes](04-ENTERPRISE-SCALING.md)
- [API cache gateway](05-API-GATEWAY.md)
- [Command reference](03-MIGRATION-GUIDE.md#quick-reference)
- [Aegis hardening](07-AEGIS-PROTOCOL.md)

---

## Glossary

| Term | Meaning |
|------|---------|
| **Fluid routing** | Traffic smoothing via viscosity delays instead of connection drops |
| **Zero-config** | Utahx detects project type from files in the folder |
| **Semantic pre-fetch** | Predicts next page from pointer movement and pre-loads it |
| **Semantic cache** | RAM store keyed by hash of path + request body |
| **ACME** | Automated certificate authority protocol (Let's Encrypt) |
| **Aegis** | TCP hardening: timeouts, max connections, graceful SIGTERM drain |

---

## Contributing to docs

Documentation changes belong in the language-specific folder only. Do not mix languages on one page. Add new locales as sibling directories (`tdocs/`, `cdocs/`, `edocs/`, `fdocs/`, and so on).

---

## Other languages (separate folders)

Each translation is isolated in its own directory. Pages contain **one language only**.

| Language | Index |
|----------|-------|
| Russian | [../tdocs/README.md](../tdocs/README.md) |
| Chinese (Simplified) | [../cdocs/README.md](../cdocs/README.md) |
| Estonian | [../edocs/README.md](../edocs/README.md) |
| Finnish | [../fdocs/README.md](../fdocs/README.md) |
