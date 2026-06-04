# Utahx Official Documentation — Part 4: Enterprise Scaling (Docker & Kubernetes)

**Audience:** DevOps, platform engineers  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## The Analogy: Magic Butler and the Cloning Factory

One Utahx instance runs your site perfectly. At planetary scale, you clone identical **stateless** Utahx nodes inside sealed **Docker** boxes, and **Kubernetes** scales replicas when CPU exceeds 70%.

---

## Step-by-Step

| Step | Command / file |
|------|----------------|
| 1 | `Dockerfile` — packs Utahx into a slim Python 3.11 image |
| 2 | `docker build -t utahisnotastate/utahx:latest .` |
| 3 | `deploy/utahx_kubernetes_scale.yaml` — Deployment (3 replicas) + HPA (3–100) |
| 4 | `kubectl apply -f deploy/utahx_kubernetes_scale.yaml` |

---

## Docker (local)

```bash
docker build -t utahisnotastate/utahx:latest .
docker run -p 8080:8080 -v $(pwd)/site:/app/site -w /app/site utahisnotastate/utahx:latest
```

Or:

```bash
docker compose up --build
```

---

## Kubernetes

- **Service** maps port `80` → container `8080`
- **HPA** scales `utahx-gateway` from **3** to **100** pods at **70% CPU**
- Set `UTAHX_STATELESS=1` — no local state required for routing pods

TLS certificates and `.utahx/vault` should be mounted via Secrets in production, or terminated at the cloud load balancer.

---

## Professional Pivot

Utahx is **stateless** at the edge: fluid metrics and semantic cache are per-pod RAM (ephemeral). Horizontal scaling does not require shared disk. For shared semantic cache at scale, front Redis via Utahx Cloud (Part 6).

Next: [Part 5 — API Gateway & Semantic Cache](05-API-GATEWAY.md)
