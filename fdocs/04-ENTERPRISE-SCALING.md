# Osa 4: Yrityskaala (Docker ja Kubernetes)

**Kohderyhmä:** DevOps ja alustain insinöörit  
**Repositorio:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Vertaus: kloonaustehdas

Yksi Utahx-instanssi riittää normaalikuormaan. Viraalipiikissä Utahx pakataan **Docker**-konteihin ja **Kubernetes** kloonaa instansseja CPU:n noustessa — ilman käsityönä kopioitavia Nginx-konfiguraatioita.

---

## Periaatteet

| Periaate | Toteutus |
|----------|----------|
| **Tilaton** | `UTAHX_STATELESS=1` |
| **Vaakaskaalaus** | HPA 3→100 podia @ 70 % CPU |
| **Kevyt kuva** | `python:3.11-slim` |
| **Nollakonfiguraatio** | CLI kontissa |

Välimuisti ja nestemittarit ovat podin RAM:ssa. Jaettu välimuisti: Redis tai Utahx Cloud (osa 6).

---

## Docker

### Rakenna

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
docker build -t utahisnotastate/utahx:latest .
```

### Aja

```bash
mkdir site && echo '<h1>Hei</h1>' > site/index.html
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

Manifesti: `deploy/utahx_kubernetes_scale.yaml`

| Resurssi | Tarkoitus |
|----------|-----------|
| `Service` (LoadBalancer) | **80** → pod **8080** |
| `Deployment` | **3** replikaa |
| `HorizontalPodAutoscaler` | **3–100**, **70 %** CPU |

### Ota käyttöön

```bash
kubectl apply -f deploy/utahx_kubernetes_scale.yaml
kubectl get pods -l app=utahx
kubectl get hpa utahx-auto-scaler
```

### Tuotanto

- TLS pilven load balancerissa tai Secret podissa  
- Sisältö Volume/ConfigMap-kautta  
- Säädä CPU/RAM-rajat  
- Käytä manifestin probeja  

---

## Monialuehuomio

Aja erilliset Utahx-deployt alueittain geo-DNS:n tai globaalin load balancerin takana. Jaettu semanttinen välimuisti alueiden välillä vaatii Utahx Cloudin tai hallitun Redis-kerroksen.

---

## CI/CD

`.github/workflows/ci.yml` ajaa testit jokaisella pushilla.

---

## Havainnointi

| Signaali | Missä |
|----------|-------|
| Turbulenssi | Utahx-lokit |
| Välimuisti | `X-Utahx-Cache` |
| TLS | `UtahxSecurity` |
| Versio | `UtahxRegistry` käynnistyksessä |

---

## Vianetsintä

| Oire | Tarkista |
|------|----------|
| CrashLoop | Portti 8080; mount |
| SPA 404 | `--static`; `index.html` |
| TLS dev -varoitus | Odotettu self-signed; tuotannossa ACME |
| HPA ei skaalaa | Metrics Server; CPU requests |

---

## Seuraavaksi

- [Osa 5](05-API-GATEWAY.md)  
- [Osa 6](06-MONETIZATION.md)
