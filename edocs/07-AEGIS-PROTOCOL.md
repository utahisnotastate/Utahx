# Osa 7: Aegise protokoll (serva tugevdamine)

**Sihtrühm:** Turva-insenerid, SRE  
**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)  
**Moodul:** `utahx_core_aegis.py`

---

## Miks Aegis

„Hello World“ on nädalavahetuse projekt. **Pahatahtlik internet** nõuab ettevõtte taset: Slowloris, ühenduste laviin, veidrud kliendid, taaskäivitus ilma aktiivsete katkestusteta.

Aegis on Utahxi **TCP tugevdus** vedeliku routeri kohal.

---

## Analoogia: restorani nali

| Oht | Ilma Aegiseta | Aegis-ga |
|-----|---------------|----------|
| **Slowloris** | Järjekord seisab | 5 s lugemise aegumine |
| **Veider klient** | Töötaja hangub | Aegumine + isoleerimine |
| **TCP laviin** | RAM otsas | Semafor (vaikimisi 1000) |
| **Taaskäivitus** | Kõik katkevad | Pehme sulgemine: kuni 30 s drain |

---

## Kolm kaitset

1. **Taimer** — `network_timeout=5.0`  
2. **Ühenduspiir** — `max_connections=1000`  
3. **Pehme sulgemine** — `drain_timeout=30.0`, SIGINT/SIGTERM

---

## Kasutus

```bash
python utahx_core_aegis.py
```

`start_utahx` kasutab Aegist **vaikimisi**; `aegis=False` legacy režiim.

---

## Logid

`utahx_access.log` + konsool.

---

## Testid

```bash
python -m unittest test_utahx_aegis -v
```

---

## Seotud

- [Osa 3](03-MIGRATION-GUIDE.md)  
- [Indeks](README.md)
