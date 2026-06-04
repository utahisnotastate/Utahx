# Utahx dokumentatsioon (eesti keel)

Utahx SOTA veebimootori ametlik dokumentatsioon.

**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Dokumentatsiooni kaart

| Osa | Dokument | Sihtrühm |
|-----|----------|----------|
| 1 | [01-CHILD-PROTOCOL.md](01-CHILD-PROTOCOL.md) | Algajad ja mitte-tehnilised kasutajad |
| 2 | [02-BUSINESS-GUIDE.md](02-BUSINESS-GUIDE.md) | Asutajad, tooteomanikud, operaatorid |
| 3 | [03-MIGRATION-GUIDE.md](03-MIGRATION-GUIDE.md) | DevOps, SRE, backend-insenerid |
| 4 | [04-ENTERPRISE-SCALING.md](04-ENTERPRISE-SCALING.md) | Docker ja Kubernetes |
| 5 | [05-API-GATEWAY.md](05-API-GATEWAY.md) | API omanikud ja backend |
| 6 | [06-MONETIZATION.md](06-MONETIZATION.md) | Utahx Cloud monetiseerimine |
| 7 | [07-AEGIS-PROTOCOL.md](07-AEGIS-PROTOCOL.md) | Aegis TCP tugevdus |

---

## Soovitatav lugemisjärjekord

1. **Esimene veebisait?** Alusta osast 1.  
2. **Äri ja tulu?** Osa 2, seejärel osa 3.  
3. **Nginx asendamine?** Otse osa 3.  
4. **Miljonite kasutajate skaala?** Osad 4 ja 5.  
5. **Toot ettevõte Utahx ümber?** Osa 6.

---

## Mida Utahx asendab

Üks CLI asendab käsitsi **Nginx seadistuse**, **Certbot töövoogud**, lihtsa **pöördproksi** ja jäika **ühenduslimiidi** järgmisega:

- Vedeliku sarnane liikluse silumine (ühendusi ei katkestata)
- Nullkonfiguratsiooniga projekti tuvastus
- Autonoomne TLS
- Inimloetavad vealehed
- HTML semantiline eellaadimine
- JSON API semantiline RAM vahemälu
- Tootmiseks valmis Docker ja Kubernetes manifestid

---

## Kiirlingid

- [Paigaldus ja esimene käivitus](03-MIGRATION-GUIDE.md#paigaldus)
- [Docker ja Kubernetes](04-ENTERPRISE-SCALING.md)
- [API vahemälu lüüs](05-API-GATEWAY.md)
- [Käskude lühiülevaade](03-MIGRATION-GUIDE.md#käskude-lühiülevaade)

---

## Teised keeled (eraldi kaustad)

Igal lehel on **ainult üks keel**.

| Keel | Indeks |
|------|--------|
| English | [../docs/README.md](../docs/README.md) |
| Русский | [../tdocs/README.md](../tdocs/README.md) |
| 简体中文 | [../cdocs/README.md](../cdocs/README.md) |
| Suomi | [../fdocs/README.md](../fdocs/README.md) |
