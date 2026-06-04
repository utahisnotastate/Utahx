# Osa 6: Monetiseerimise plaan (Utahx Cloud)

**Sihtrühm:** Asutajad, müük, ettevõttemüük  
**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Strateegia

Utahx avatud lähtekood eemaldab Nginx valu. **Utahx Cloud Control** müüb seda, mille eest ettevõtted maksavad: nähtavus, globaalne poliitika, hallatud skaala, tugi.

```
Tasuta OSS  →  Arendajate kasutuselevõtt  →  Cloud tellimus
```

---

## Toode: Utahx Cloud Control

### Paketid

| Pakett | Hind | Sisaldab |
|--------|------|----------|
| **Hobbyist** | Tasuta | Kohalik Utahx, kogukond, põhilogid |
| **Pro** | $99/kuu (plaan) | Dashboard, e-posti alertid, 30 päeva mõõdikud |
| **Enterprise** | $499/kuu | Ohtude blokeerimine, globaalne kaart, ühe klõpsuga GKE/EKS, Redis vahemälu, SSO, SLA |

### Valu → tasuline

| Valu | Cloud |
|------|-------|
| „Kas maailmas töötab?“ | Globaalne soojuskaart |
| „Peata kohe“ | API võti kill switch |
| „Skaala ilma YAML“ | `utahx_kubernetes_scale.yaml` ühe nupuga |
| „Miks API aeglane?“ | Cache HIT ja viskoossus |
| „Compliance“ | Audit, RBAC, SSO |

---

## Turule toomine

### Faas 1 (nädal 1–2)

1. Avalda: [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
2. Pealkiri: *„Nginx on surnud. Nullkonfiguratsiooniga veebimootor.“*  
3. CTA: `git clone` + `utahx start`  

### Faas 2 (nädal 3–8)

- GHCR pilt  
- DevRel: „Migratsioon 60 sekundiga“  
- GitHub Issues tagasiside  

### Faas 3 (kuu 3+)

- Cloud beta  
- `UTAHX_CLOUD_API_KEY` (teekaart)  
- Enterprise müük K8s klientidele  

---

## Tehniline haak (teekaart)

```bash
export UTAHX_CLOUD_API_KEY=utx_live_xxxxxxxx
utahx start --domain example.com
```

Plaanitud telemeetria: RPS, viskoossus, cache HIT, TLS, podide arv.

---

## Tulu mudel

| Voog | Mudel |
|------|-------|
| OSS | MIT |
| Cloud | Kuutasu organisatsioonile |
| Managed | K8s namespace ülekasutus |
| Enterprise | Aastaleping + tugi |

---

## Dokumentatsioon

- [Eesti indeks](README.md)  
- [English](../docs/README.md)  
- [Русский](../tdocs/README.md)  
- [简体中文](../cdocs/README.md)  
- [Suomi](../fdocs/README.md)
