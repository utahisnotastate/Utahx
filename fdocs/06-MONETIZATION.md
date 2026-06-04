# Osa 6: Kaupallistamissuunnitelma (Utahx Cloud)

**Kohderyhmä:** Perustajat, myynti, yritysmyynti  
**Repositorio:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Strategia

Utahx avoin lähdekoodi poistaa Nginx-kivun. **Utahx Cloud Control** myy sitä, mistä yritykset maksavat: näkyvyys, globaali politiikka, hallittu skaala, tuki.

```
Ilmainen OSS  →  Kehittäjäkäyttöönotto  →  Cloud-tilaus
```

---

## Tuote: Utahx Cloud Control

### Tasot

| Taso | Hinta | Sisältää |
|------|-------|----------|
| **Hobbyist** | Ilmainen | Paikallinen Utahx, yhteisö, peruslokit |
| **Pro** | $99/kk (suunnitelma) | Dashboard, sähköpostihälytykset, 30 päivän mittarit |
| **Enterprise** | $499/kk | Uhkien esto, globaali kartta, GKE/EKS yhdellä napsautuksella, Redis-välimuisti, SSO, SLA |

---

## Markkinoilletulo

### Vaihe 1 (viikot 1–2)

1. Julkaise: [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
2. Otsikko: *„Nginx on kuollut. Nollakonfiguraation verkkomoottori.“*  
3. CTA: `git clone` + `utahx start`  

### Vaihe 2 (viikot 3–8)

- GHCR-kuva  
- DevRel: „Migraatio 60 sekunnissa“  
- GitHub Issues -palaute  

### Vaihe 3 (kk 3+)

- Cloud-beta  
- `UTAHX_CLOUD_API_KEY` (tiekartta)  
- Enterprise-myynti K8s-asiakkaille  

---

## Tekninen koukku (tiekartta)

```bash
export UTAHX_CLOUD_API_KEY=utx_live_xxxxxxxx
utahx start --domain example.com
```

Suunniteltu telemetria: RPS, viskositeetti, cache HIT, TLS, podien määrä.

---

## Tulomalli

| Lähde | Malli |
|-------|-------|
| OSS | MIT |
| Cloud | Kuukausimaksu organisaatiolle |
| Managed | K8s-namespace ylikulutus |
| Enterprise | Vuosisopimus + tuki |

---

## Dokumentaatio

- [Suomi](README.md)  
- [English](../docs/README.md)  
- [Русский](../tdocs/README.md)  
- [简体中文](../cdocs/README.md)  
- [Eesti](../edocs/README.md)
