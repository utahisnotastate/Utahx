# Osa 5: Edistynyt API-yhdyskäytävä

**Kohderyhmä:** Backend-insinöörit ja API-omistajat  
**Repositorio:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Miksi Utahx-yhdyskäytävä

Nginx välimuistittaa **tarkan URL:n**. Utahx **semanttinen välimuisti** laskee sormenjäljen **polusta + rungosta**.

Kerros on **reunalla**, ennen sovelluksen worker-poolia.

---

## Komponentit

| Luokka | Tiedosto | Rooli |
|--------|----------|-------|
| `SemanticMemoryCore` | `utahx_cache.py` | Vault: sormenjälki → (tavut, vanheneminen) |
| `SemanticCacheMiddleware` | `utahx_cache.py` | HTTP-middleware |

---

## Säännöt

| Sääntö | Arvo |
|--------|------|
| Metodit | `GET`, `HEAD` |
| Polut | `/api/*` tai `Accept: application/json` |
| Ohita | `/__utahx/*` |
| Tallenna | HTTP **200** |
| TTL | **60** s |

---

## Turvallisuus

Välimuisti tallentaa koko vastausruumiin prosessin muistiin. Älä ota välimuistia käyttöön tunnistetuille päätepisteille, jotka palauttavat käyttäjäkohtaista dataa, ellei pyynnön runko yksilöi subjektia täysin ja TTL ole hyväksyttävä.

---

## Python

```python
from utahx_auto import UtahxServer

server = UtahxServer(
    directory=".",
    cache_ttl_seconds=300,
    enable_semantic_cache=True,
)
server.start(port=8080)
```

Poista käytöstä:

```python
UtahxServer(directory=".", enable_semantic_cache=False)
```

---

## Täysi reunapino (v1.2)

```
HTTP-pyyntö
    → HumanIntrospectionMiddleware
    → FluidTrafficMiddleware
    → SemanticCacheMiddleware
    → PrefetchInjectMiddleware
    → Sovellus
```

---

## Kapasiteettisuunnittelu

| Tekijä | Ohje |
|--------|------|
| RAM | Koko vastaus TTL:ään asti |
| Kardinaliteetti | Enemmän runkoja → alempi HIT |
| Invalidointi | Tällä hetkellä vain TTL |
| Useita podeja | Redis klusterissa |

---

## Testit

```bash
python -m unittest test_utahx_cache -v
```

---

## Liittyvät

- [Osa 3](03-MIGRATION-GUIDE.md)  
- [Osa 4](04-ENTERPRISE-SCALING.md)
