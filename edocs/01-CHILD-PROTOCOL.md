# Osa 1: Lihtne protokoll (Child-Protocol)

**Sihtrühm:** Algajad ja mitte-tehnilised kasutajad  
**Hoidla:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Analoogia: automaatne poe esikülg

Kujuta ette, et teed garaažis puidust sildi limonaadiputka jaoks.

**Vana viis (Nginx jms):** pead palgama brigaadi, taotlema lube, palgama turvamehe ja ehitama tee, enne kui keegi su silti näeb. Üks kirjaviga seadistusfailis võib ukse lukku panna. See võtab päevi või nädalaid.

**Utahx viis:** paned sildi „maagilisse kasti“, vajutad ühte nuppu — putka ilmub tihedale tänavale ja turvamees on juba kohal.

Utahx on see kast veebisaitide jaoks.

---

## Mida vajad enne alustamist

- Arvuti (Windows, Mac või Linux)
- Kaust veebifailidega (vähemalt `index.html`)
- Valikuline: sinu domeen (nt `minupood.ee`)

**Ei pea** oskama programmeerida ega Nginx/SSL-i.

---

## Samm-sammult: esimene veebisait

| Samm | Tegevus |
|------|---------|
| 1 | Loo töölaual kaust `MinuVeeb`. |
| 2 | Kopeeri sinna saidi failid (`index.html`, pildid jne). |
| 3 | Laadi Utahx alla [GitHubist](https://github.com/utahisnotastate/Utahx) ja pane `utahx.cmd` või `utahx.exe` kausta `MinuVeeb`. |
| 4 | Topeltklõpsa Utahx failil. |
| 5 | Domeeni küsimisel sisesta oma domeen või vajuta **Enter** (ainult kohalik test). |

**Valmis.** Utahx skaneerib kausta, valib serveerimisviisi ja käivitab serveri. Domeeniga seadistatakse ka HTTPS.

Ilma domeenita on sait tavaliselt aadressil `http://localhost:8080`.

---

## Mida Utahx automaatselt teeb

| Funktsioon | Sinu jaoks |
|------------|------------|
| **Autotuvastus** | Tunneb ära HTML, Python või Node.js |
| **Autoturvalisus** | Domeeniga taotleb TLS sertifikaate |
| **Liikluse silumine** | Tipu ajal viivitab pisut, mitte ei näita 502 |
| **Eellaadimine** | Ennustab järgmist lehte ja laadib ette |
| **Sõbralikud vead** | Selged ekraanid, mitte `502 Bad Gateway` |

---

## Korduma kippuvad küsimused

**Kas vajan seadistusfaili?**  
Ei. Utahx väldib tahtlikult `nginx.conf` tüüpi faile.

**Kas sait on avalikus internetis?**  
Jah, kui DNS osutab sinu serverile ja portid 80/443 on avatud.

**Mis juhtub vea korral?**  
Utahx näitab arusaadavat teksti; arendaja näeb faili ja rea vihjet.

---

## Professionaalne tähendus (lihtsas keeles)

Utahx töötab **pöördproksina** ja **veebiserverina** portidel **80** ja **443**, skaneerib projekti kausta ja suunab külastajaid — **ilma käsitsi konfiguratsioonita**.

---

## Kiire abi

| Probleem | Proovi |
|----------|--------|
| Tühi leht kohalikult | Ava `http://localhost:8080`; kontrolli `index.html` |
| Domeen ei tööta | DNS A/AAAA kirje serverisse; tulemüür |
| Windows aken sulgub kohe | Käivita terminalis: `py -3.11 utahx_launcher.py` |

---

## Edasi

- Äri: [Osa 2 — Ärijuhend](02-BUSINESS-GUIDE.md)  
- Tehnika: [Osa 3 — Migreerimine](03-MIGRATION-GUIDE.md)  
- Indeks: [edocs/README.md](README.md)
