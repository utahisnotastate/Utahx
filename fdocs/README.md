# Utahx-dokumentaatio (suomi)

Utahx SOTA -verkkomoottorin virallinen dokumentaatio.

**Repositorio:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Dokumentaatiokartta

| Osa | Dokumentti | Kohderyhmä |
|-----|------------|------------|
| 1 | [01-CHILD-PROTOCOL.md](01-CHILD-PROTOCOL.md) | Aloittelijat ja ei-tekniset käyttäjät |
| 2 | [02-BUSINESS-GUIDE.md](02-BUSINESS-GUIDE.md) | Perustajat, tuoteomistajat, operaattorit |
| 3 | [03-MIGRATION-GUIDE.md](03-MIGRATION-GUIDE.md) | DevOps, SRE, backend-insinöörit |
| 4 | [04-ENTERPRISE-SCALING.md](04-ENTERPRISE-SCALING.md) | Docker ja Kubernetes |
| 5 | [05-API-GATEWAY.md](05-API-GATEWAY.md) | API-omistajat ja backend |
| 6 | [06-MONETIZATION.md](06-MONETIZATION.md) | Utahx Cloud -kaupallistaminen |
| 7 | [07-AEGIS-PROTOCOL.md](07-AEGIS-PROTOCOL.md) | Aegis TCP-kovennus |
| 8 | [08-APEX-PROTOCOL.md](08-APEX-PROTOCOL.md) | Apex botit ja deploy |

---

## Suositeltu lukujärjestys

1. **Ensimmäinen verkkosivu?** Aloita osasta 1.  
2. **Liiketoiminta ja tulot?** Osa 2, sitten osa 3.  
3. **Nginxin korvaaminen?** Suoraan osa 3.  
4. **Miljoonien käyttäjien skaala?** Osat 4 ja 5.  
5. **Tuoteyritys Utahxin ympärille?** Osa 6.

---

## Mitä Utahx korvaa

Yksi CLI korvaa manuaalisen **Nginx-konfiguroinnin**, **Certbot-työnkulut**, yksinkertaisen **käänteisen välityspalvelimen** ja jäykät **yhteysrajat**:

- Nestemäinen liikenteen tasoitus (ei katkaise yhteyksiä)
- Nollakonfiguraation projektintunnistus
- Autonominen TLS
- Ihmiselle luettavat virhesivut
- HTML-semanttinen esihaku
- JSON API -semanttinen RAM-välimuisti
- Tuotantovalmiit Docker- ja Kubernetes-manifestit

---

## Pikalinkit

- [Asennus ja ensimmäinen käynnistys](03-MIGRATION-GUIDE.md#asennus)
- [Docker ja Kubernetes](04-ENTERPRISE-SCALING.md)
- [API-välimuistin yhdyskäytävä](05-API-GATEWAY.md)
- [Komentopikaopas](03-MIGRATION-GUIDE.md#komentopikaopas)

---

## Muut kielet (erilliset kansiot)

Jokaisella sivulla on **vain yksi kieli**.

| Kieli | Hakemisto |
|-------|-----------|
| English | [../docs/README.md](../docs/README.md) |
| Русский | [../tdocs/README.md](../tdocs/README.md) |
| 简体中文 | [../cdocs/README.md](../cdocs/README.md) |
| Eesti | [../edocs/README.md](../edocs/README.md) |
