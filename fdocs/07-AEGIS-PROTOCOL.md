# Osa 7: Aegis-protokolla (reunan kovennus)

**Kohderyhmä:** Tietoturvainsinöörit, SRE  
**Repositorio:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
**Moduuli:** `utahx_core_aegis.py`

---

## Miksi Aegis

„Hello World“ on viikonlopun projekti. **Ilkeä internet** vaatii yritystason tekniikkaa: Slowloris, yhteysfloodi, outoja asiakkaita, uudelleenkäynnistys ilman aktiivisten katkaisuja.

Aegis on Utahxin **TCP-kovennus** nestemäisen reitittimen päällä.

---

## Vertaus: ravintolan kepposet

| Uhka | Ilman Aegista | Aegisin |
|------|---------------|---------|
| **Slowloris** | Jono pysähtyy | 5 s lukuaikakatko |
| **Outo asiakas** | Työntekijä jumissa | Aikakatko + eristys |
| **Yhteysfloodi** | RAM loppuu | Semafori (oletus 1000) |
| **Uudelleenkäynnistys** | Kaikki katkeaa | Pehmeä sulkeminen: 30 s drain |

---

## Kolme puolustusta

1. **Ajastin** — `network_timeout=5.0`  
2. **Yhteysraja** — `max_connections=1000`  
3. **Pehmeä sulkeminen** — `drain_timeout=30.0`, SIGINT/SIGTERM

---

## Käyttö

```bash
python utahx_core_aegis.py
```

`start_utahx` käyttää Aegista **oletuksena**; `aegis=False` legacy-tila.

---

## Lokitus

`utahx_access.log` + konsoli.

---

## Testit

```bash
python -m unittest test_utahx_aegis -v
```

---

## Liittyvät

- [Osa 3](03-MIGRATION-GUIDE.md)  
- [Hakemisto](README.md)
