# Osa 3: Tehniline migreerimisjuhend

**Sihtrühm:** DevOps, SRE, backend-insenerid  
**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

Utahx asendab Nginx **konfiguratsioonifailid** ühe CLI käsuga. Enamik migratsioone **alla 60 sekundi** pärast paigaldust.

> **Märkus:** Pärast `pip install -e .` kasuta `utahx start`. Sama lipud: `python -m utahx_cli start`.

---

## Paigaldus

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
pip install -e .
```

### Nõuded

- Python **3.11+**
- `requirements.txt` sõltuvused
- Valikuline ACME: `pip install -e ".[secure]"`

Kontroll:

```bash
python -m unittest discover -v
```

---

## Stsenaarium A: pöördproksi (Node.js, Python, Go)

### Enne: Nginx

```nginx
server {
    listen 80;
    server_name example.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Pärast: Utahx

```bash
cd /path/to/your/app
utahx start --proxy 5000 --domain example.com --email ops@example.com
```

| Seade | Käitumine |
|-------|-----------|
| Kuulamine | **443** TLS-iga `--domain`-iga; **8080** kohalikult |
| Upstream | `http://127.0.0.1:5000` |
| Serva kaitse | FluidTrafficMiddleware |
| HTML | Eellaadimise skripti süst |

Rakendus peab juba kuulama sihtporti.

---

## Stsenaarium B: staatiline sait / SPA

```bash
cd ./dist
utahx start --static --domain example.com
```

| Seade | Käitumine |
|-------|-----------|
| Režiim | Sunnitud staatika |
| SPA | Tundmatu tee → `index.html` |
| Eellaadimine | `/__utahx/prefetch/*` |

---

## Stsenaarium C: nullkonfiguratsioon

```bash
cd /path/to/project
utahx start
```

Järjekord: `package.json` → Node; `requirements.txt` / `main.py` → Python; `index.html` → staatika.

---

## Middleware voog

```
Klient
  → HumanIntrospectionMiddleware
  → FluidTrafficMiddleware
  → SemanticCacheMiddleware
  → PrefetchInjectMiddleware
  → Staatika | proksi | autobackend
```

---

## Semantiline eellaadimine

| Endpoint | Meetod | Otstarve |
|----------|--------|----------|
| `/__utahx/prefetch/manifest?path=/` | GET | Linkide graaf |
| `/__utahx/prefetch/signal` | POST | Kursor → URL-id |
| `/__utahx/prefetch/utahx.js` | GET | Brauseri skript |

---

## Semantiline vahemälu

| Päis | Tähendus |
|------|----------|
| `X-Utahx-Cache: HIT` | RAM-ist |
| `X-Utahx-Cache: MISS` | Backend + salvestus |

Vaikimisi TTL **60 s**. `UtahxServer(cache_ttl_seconds=120)`.

---

## TLS

```bash
utahx start --domain example.com --email admin@example.com
```

---

## Windows

1. Kopeeri projekt + `utahx.cmd` ühte kausta.  
2. Topeltklõps (interaktiivne domeen).  
3. `.\scripts\build_utahx_exe.ps1`

---

## Keskkonnamuutujad

| Muutuja | Otstarve |
|---------|----------|
| `UTAHX_STATELESS` | `1` konteineris |
| `UTAHX_PORT` | Dockeris **8080** |

---

## Käskude lühiülevaade

| Käsk | Kasutus |
|------|---------|
| `utahx start` | Autotuvastus |
| `utahx start --static --domain example.com` | SPA / staatika |
| `utahx start --proxy 5000 --domain example.com` | Rakendus port 5000 |
| `utahx start --domain example.com --email ops@example.com` | TLS + ACME |
| `utahx start --port 9000` | Kohandatud port |

---

## Seotud

- [Osa 4](04-ENTERPRISE-SCALING.md)  
- [Osa 5](05-API-GATEWAY.md)  
- [Osa 6](06-MONETIZATION.md)  
- [Indeks](README.md)
