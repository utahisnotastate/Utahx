# Osa 2: Äri- ja ROI juhend

**Sihtrühm:** Asutajad, tooteomanikud, operaatorid  
**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

Sulle on oluline **tööaeg**, **turvalisus** ja **tulu**. Utahx kaitseb neid ilma Nginx ekspertmeeskonnata.

---

## Kokkuvõte juhtkonnale

| Tüüpiline Nginx risk | Utahx tulemus |
|----------------------|---------------|
| Tipuliiklus → 502, kaotatud müük | Vedeliku silumine, backend püsib töös |
| SSL aegumine → sait maas | ACME automaatne pikendamine |
| Krahh hirmutab kasutajaid | Bränditud, rahulikud vealehed |
| Aeglane navigeerimine | Semantiline eellaadimine |
| Korduvad API päringud koormavad DB-d | Semantiline vahemälu RAM-ist |

**Migratsiooni aeg:** inseneritele tavaliselt alla tunni; operaatoritele null konfiguratsioonifaili.

---

## 1. Krahhikindel liiklus (vedeliku koormusjaotus)

### Probleem

Kampaaniad ja viiruslik kasv toovad tuhandeid samaaegseid päringuid. Traditsiooniline pöördproksi **lõpetab ühendused** — **502 Bad Gateway**, klient lahkub.

### Utahx lahendus

Liiklus käitub nagu vedelik: ülekoormusel **millisekundiline viivitus**, mitte katkestus. Rakendusserverid jäävad kõrge koormuse juurde ilma kokkuvarisemiseta.

**ROI:** rohkem ostu tipu ajal; vähem „sait on maas“ postitusi.

---

## 2. HTTPS ilma sertifikaadi kalendrita

### Probleem

Certbot, `.pem` failid, meeldetuletused — inimvead põhjustavad brauseri hoiatuse ja SEO kahju.

### Utahx lahendus

Üks kord domeen — Utahx taotleb **ACME v2** sertifikaate, salvestab `.utahx/vault/` ja laadib taaskäivitusel.

**ROI:** vähem sertifikaadi seisakuid; vähem auditiriske.

---

## 3. Usaldust säilitavad vead (introspektsioon)

Rakenduse tõrge → **tume HTML** selge pealkirja ja arendajavihjega (fail + rida), ilma stack trace’ita lõppkasutajale.

**ROI:** vähem põgenemist vealehtedelt; kiirem parandus.

---

## 4. Kiirus kui eelis (semantiline eellaadimine)

Hiire liikumise ja linkide põhjal ennustatakse järgmist klõpsu ja **eel-laaditakse** sisu.

---

## 5. API efektiivsus (semantiline vahemälu)

Identsed päringud (tee + keha) vastatakse **RAM-ist**. Päised `X-Utahx-Cache: HIT` / `MISS`.

---

## 6. Skaala ilma uute operaatoriteta

Repos on Docker ja Kubernetes. HPA skaleerib **3–100** podi CPU **70%** juures.

Detailid: [Osa 4](04-ENTERPRISE-SCALING.md)

---

## TCO lühivaade

| Kulu rida | Nginx + Certbot | Utahx OSS |
|-----------|-----------------|-----------|
| Inseneriaastad konfig + sertid | 40–120 h | 5–20 h |
| Seisakud limiit/sert | Kõrgem | Madalam |

---

## Juhtkonna kontrollnimekiri

- [ ] Kaotame müüki tipus? → Vedeliku routing  
- [ ] Sertifikaadi seisak viimase 12 kuu jooksul? → Auto-TLS  
- [ ] Tugipiletid pärast releasi? → Sõbralikud vead  
- [ ] SPA aeglane? → Eellaadimine  
- [ ] API read kallis? → Semantiline vahemälu  

---

## Edasi

- Migreerimine: [Osa 3](03-MIGRATION-GUIDE.md)  
- Utahx Cloud: [Osa 6](06-MONETIZATION.md)
