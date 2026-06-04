# Part 4: Enterprise Scaling (Docker and Kubernetes)

**Audience:** DevOps and platform engineers  
**Repository:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## The analogy: cloning factory

One Utahx instance handles normal load. At viral scale you seal Utahx in **Docker** containers and let **Kubernetes** clone them when CPU rises. You do not provision VMs by hand or copy Nginx configs to each machine.

---

## Design principles

| Principle | Implementation |
|-----------|----------------|
| **Stateless pods** | No required local disk; `UTAHX_STATELESS=1` |
| **Horizontal scale** | HPA adds pods from 3 to 100 at 70% CPU |
| **Thin image** | `python:3.11-slim` base |
| **Config-free runtime** | CLI starts server inside container |

Per-pod RAM holds fluid metrics and semantic cache entries. For shared cache at cluster scale, use Utahx Cloud or external Redis (see Part 6).

---

## Docker

### Build

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
docker build -t utahisnotastate/utahx:latest .
```

### Run (single container)

```bash
mkdir site && echo '<h1>Hello</h1>' > site/index.html
docker run --rm -p 8080:8080 \
  -v "$(pwd)/site:/app/site:ro" \
  -w /app/site \
  utahisnotastate/utahx:latest
```

Open `http://localhost:8080`.

### Docker Compose

```bash
docker compose up --build
```

Edit `docker-compose.yml` to mount your site directory under `/app/site`.

---

## Kubernetes

Manifest: `deploy/utahx_kubernetes_scale.yaml`

### Components

| Resource | Purpose |
|----------|---------|
| `Service` (LoadBalancer) | Exposes port **80** → pod **8080** |
| `Deployment` | **3** replicas by default |
| `HorizontalPodAutoscaler` | Scales **3–100** replicas at **70%** CPU |

### Deploy

```bash
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
kubectl get pods -l app=utahx
kubectl get hpa utahx-auto-scaler
```

### Production notes

- Terminate TLS at cloud load balancer **or** mount TLS Secrets into pods  
- Mount application content via ConfigMap/Volume or run Utahx in front of a separate app Service  
- Set resource requests/limits per your SLO (defaults: 250m CPU request, 1Gi limit)  
- Use liveness/readiness probes already defined in the manifest  

---

## CI/CD integration

GitHub Actions workflow `.github/workflows/ci.yml` runs the full Python test suite on every push.

Suggested release pipeline:

1. Run tests  
2. `docker build` and push to registry  
3. `kubectl set image deployment/utahx-gateway utahx-node=...`  

---

## Observability hooks

| Signal | Where |
|--------|-------|
| Fluid turbulence | Utahx logs (`Turbulence detected`) |
| Cache | Response header `X-Utahx-Cache` |
| TLS | Logs from `UtahxSecurity` logger |
| Registry version | Startup log from `UtahxRegistry` |

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Pod CrashLoop | Port 8080 in container; mount valid site path |
| 403/404 on SPA | Use `utahx start --static` or ensure `index.html` exists |
| TLS warnings in dev | Expected with self-signed vault certs; use real ACME in prod |
| HPA not scaling | Metrics server installed; CPU requests set |

---

## Multi-region note

Run independent Utahx deployments per region behind geo-DNS or a global load balancer. Each region scales with its own HPA. Shared semantic cache across regions requires Utahx Cloud or a managed Redis layer (see Part 6).

---

## Next

- [Part 5 — API Gateway](05-API-GATEWAY.md)  
- [Part 6 — Monetization](06-MONETIZATION.md)
