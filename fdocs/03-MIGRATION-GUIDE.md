# Osa 3: Tekninen migraatio-opas

**Kohderyhmä:** DevOps, SRE, backend-insinöörit  
**Repositorio:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

Utahx korvaa Nginx-**konfiguraatiotiedostot** yhdellä CLI-komennolla. Useimmat migraatiot alle **60 sekunnissa** asennuksen jälkeen.

> **Huom:** `pip install -e .` jälkeen käytä `utahx start`. Samat liput: `python -m utahx_cli start`.

---

## Asennus

```bash
git clone https://github.com/utahisnotastate/Utahx.git
cd Utahx
pip install -e .
```

### Vaatimukset

- Python **3.11+**
- `requirements.txt`-riippuvuudet
- Valinnainen ACME: `pip install -e ".[secure]"`

Tarkistus:

```bash
python -m unittest discover -v
```

---

## Skenaario A: käänteinen välityspalvelin

### Ennen: Nginx

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

### Jälkeen: Utahx

```bash
cd /path/to/your/app
utahx start --proxy 5000 --domain example.com --email ops@example.com
```

| Asetus | Käyttäytyminen |
|--------|----------------|
| Kuuntelu | **443** TLS `--domain`-illa; **8080** paikallisesti |
| Upstream | `http://127.0.0.1:5000` |
| Reunan suojaus | FluidTrafficMiddleware |
| HTML | Esihakuskriptin injektio |

---

## Skenaario B: staattinen sivu / SPA

```bash
cd ./dist
utahx start --static --domain example.com
```

---

## Skenaario C: nollakonfiguraatio

```bash
cd /path/to/project
utahx start
```

---

## Arkkitehtuurikartta

```
Internet
    │
    ▼
Utahx (80 / 443 / 8080)
    ├── HumanIntrospectionMiddleware
    ├── FluidTrafficMiddleware
    ├── SemanticCacheMiddleware
    ├── PrefetchInjectMiddleware
    ├── AutoTLSEngine
    └── Kohde: staattinen | proxy | autobackend
```

Moduulit: `utahx_cli`, `utahx_auto`, `utahx_core`, `utahx_secure`, `utahx_prefetch`, `utahx_cache`.

---

## Semanttinen esihaku

| Endpoint | Metodi | Tarkoitus |
|----------|--------|-----------|
| `/__utahx/prefetch/manifest?path=/` | GET | Linkkigraafi |
| `/__utahx/prefetch/signal` | POST | Osoitin → URL |
| `/__utahx/prefetch/utahx.js` | GET | Selainskripti |

---

## Semanttinen välimuisti

| Otsikko | Merkitys |
|---------|----------|
| `X-Utahx-Cache: HIT` | RAM |
| `X-Utahx-Cache: MISS` | Backend + tallennus |

Oletus-TTL **60 s**.

---

## TLS

```bash
utahx start --domain example.com --email admin@example.com
```

---

## Windows

1. Projekti + `utahx.cmd` samaan kansioon.  
2. Kaksoisnapsautus.  
3. `.\scripts\build_utahx_exe.ps1`

---

## Ympäristömuuttujat

| Muuttuja | Tarkoitus |
|----------|-----------|
| `UTAHX_STATELESS` | `1` kontissa |
| `UTAHX_PORT` | Docker **8080** |

---

## Komentopikaopas

| Komento | Käyttö |
|---------|--------|
| `utahx start` | Autotunnistus |
| `utahx start --static --domain example.com` | SPA / staattinen |
| `utahx start --proxy 5000 --domain example.com` | Sovellus portissa 5000 |
| `utahx start --domain example.com --email ops@example.com` | TLS + ACME |
| `utahx start --port 9000` | Oma portti |

---

## Liittyvät

- [Osa 4](04-ENTERPRISE-SCALING.md)  
- [Osa 5](05-API-GATEWAY.md)  
- [Osa 6](06-MONETIZATION.md)  
- [Hakemisto](README.md)
