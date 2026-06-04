# Osa 4: Ettevõtte skaala (Docker ja Kubernetes)

**Sihtrühm:** DevOps ja platvormimeeskond  
**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Analoogia: kloonimisfabriik

Üks Utahx instants katab tavakoormuse. Viirusliku tipu ajal pannakse Utahx **Docker** konteineritesse ja **Kubernetes** kloonib CPU tõusu korral — ilma käsitsi Nginx konfigide kopeerimiseta igale VM-ile.

---

## Põhimõtted

| Põhimõte | Rakendus |
|----------|----------|
| **Oleku puudumine** | `UTAHX_STATELESS=1` |
| **Horisontaalne skaala** | HPA 3→100 podi @ 70% CPU |
| **Kerge pilt** | `python:3.11-slim` |
| **Nullkonfiguratsioon** | CLI konteineris |

Vahemälu ja vedeliku mõõdikud on podi RAM-is. Klastriülese vahemälu jaoks Redis või Utahx Cloud (osa 6).

---

## Docker

### Ehita

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
docker build -t utahisnotastate/utahx:latest .
```

### Käivita

```bash
mkdir site && echo '<h1>Tere</h1>' > site/index.html
docker run --rm -p 8080:8080 \
  -v "$(pwd)/site:/app/site:ro" \
  -w /app/site \
  utahisnotastate/utahx:latest
```

### Docker Compose

```bash
docker compose up --build
```

---

## Kubernetes

Manifest: `deploy/utahx_kubernetes_scale.yaml`

| Ressurss | Otstarve |
|----------|----------|
| `Service` (LoadBalancer) | **80** → pod **8080** |
| `Deployment` | **3** koopiat |
| `HorizontalPodAutoscaler` | **3–100**, **70%** CPU |

### Juuruta

```bash
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
kubectl get pods -l app=utahx
kubectl get hpa utahx-auto-scaler
```

### Tootmine

- TLS pilve load balanceris või Secret podis  
- Sisu Volume/ConfigMap kaudu  
- Kohanda CPU/RAM limiite  
- Kasuta manifesti probe-sid  

---

## CI/CD

`.github/workflows/ci.yml` käivitab testid igal push-il.

Soovitatud releas:

1. Testid  
2. `docker build` + push registry  
3. `kubectl set image`  

---

## Jälgitavus

| Signaal | Kus |
|---------|-----|
| Turbulents | Utahx logid |
| Vahemälu | `X-Utahx-Cache` |
| TLS | `UtahxSecurity` |
| Versioon | `UtahxRegistry` käivitusel |

---

## Tõrkeotsing

| Sümptom | Kontroll |
|---------|----------|
| CrashLoop | Port 8080; mount |
| SPA 404 | `--static`; `index.html` |
| TLS dev hoiatus | Oodatav self-signed; tootmises ACME |
| HPA ei skaleeri | Metrics Server; CPU requests |

---

## Edasi

- [Osa 5](05-API-GATEWAY.md)  
- [Osa 6](06-MONETIZATION.md)
