# Osa 1: Yksinkertainen protokolla (Child-Protocol)

**Kohderyhmä:** Aloittelijat ja ei-tekniset käyttäjät  
**Repositorio:** [github.com/utahisnotastate/Utahx](https://github.com/utahisnotastate/Utahx)

---

## Vertaus: automaattinen myymälän julkisivu

Kuvittele, että teet puusta kyltin limonadikojulle autotallissasi.

**Vanha tapa (Nginx jne.):** pitää palkata työryhmä, hakea luvat, palkata vartija ja rakentaa tie ennen kuin kukaan näkee kylttisi. Yksi kirjoitusvirhe asetustiedostossa voi lukita oven. Se kestää päiviä tai viikkoja.

**Utahx-tapa:** laitat kyltin „taikalaatikkoon“, painat yhtä painiketta — koju ilmestyy vilkkaalle kadulle ja vartija on jo paikalla.

Utahx on tuo laatikko verkkosivuille.

---

## Mitä tarvitset ennen aloitusta

- Tietokone (Windows, Mac tai Linux)
- Kansio verkkotiedostoille (vähintään `index.html`)
- Valinnainen: oma verkkotunnus (esim. `minukauppa.fi`)

**Et tarvitse** ohjelmointia, Nginxia tai SSL-sertifikaatteja.

---

## Vaihe vaiheelta: ensimmäinen verkkosivu

| Vaihe | Toimenpide |
|-------|------------|
| 1 | Luo työpöydälle kansio `MinunSivu`. |
| 2 | Kopioi sivuston tiedostot sinne (`index.html`, kuvat jne.). |
| 3 | Lataa Utahx [GitHubista](https://github.com/utahisnotastate/Utahx) ja laita `utahx.cmd` tai `utahx.exe` kansioon `MinunSivu`. |
| 4 | Kaksoisnapsauta Utahx-tiedostoa. |
| 5 | Verkkotunnuksen kyselyssä kirjoita omasi tai paina **Enter** (vain paikallinen testi). |

**Valmis.** Utahx skannaa kansion, valitsee palvelutavan ja käynnistää palvelimen. Verkkotunnuksella myös HTTPS.

Ilman verkkotunnusta sivusto on yleensä osoitteessa `http://localhost:8080`.

---

## Mitä Utahx tekee automaattisesti

| Ominaisuus | Merkitys sinulle |
|------------|------------------|
| **Autotunnistus** | Tunnistaa HTML-, Python- tai Node.js-projektin |
| **Autoturva** | Verkkotunnuksella hakee TLS-sertifikaatit |
| **Liikenteen tasoitus** | Piikit viivästyttävät hieman, eivät näytä 502 |
| **Esihaku** | Ennustaa seuraavan sivun ja lataa etukäteen |
| **Ystävälliset virheet** | Selkeät ruudut, ei `502 Bad Gateway` |

---

## Usein kysyttyä

**Tarvitsenko asetustiedoston?**  
Ei. Utahx välttää tarkoituksella `nginx.conf`-tyyppisiä tiedostoja.

**Toimiiko sivu julkisessa internetissä?**  
Kyllä, jos DNS osoittaa palvelimeesi ja portit 80/443 ovat auki.

**Mitä jos jotain menee pieleen?**  
Utahx näyttää ymmärrettävän tekstin; kehittäjä näkee tiedoston ja rivin vihjeen.

---

## Turvallisuusmuistutus

Utahx altistaa tietokoneesi tai palvelimesi verkolle julkisilla porteilla. Käytä tuotannossa verkkotunnusta ja TLS:ää, päivitä käyttöjärjestelmä ja älä paljasta hallintatyökaluja ilman tunnistautumista.

---

## Ammattimainen tiivistelmä

Utahx toimii **käänteisenä välityspalvelimena** ja **verkkopalvelimena** porteissa **80** ja **443**, skannaa projektikansion ja ohjaa kävijät — **ilman käsikonfiguraatiota**.

---

## Pikavianetsintä

| Ongelma | Kokeile |
|---------|---------|
| Tyhjä sivu paikallisesti | Avaa `http://localhost:8080`; tarkista `index.html` |
| Verkkotunnus ei toimi | DNS A/AAAA palvelimeen; palomuuri |
| Windows-ikkuna sulkeutuu | Terminaalissa: `py -3.11 utahx_launcher.py` |

---

## Seuraavaksi

- Liiketoiminta: [Osa 2 — Liiketoimintaopas](02-BUSINESS-GUIDE.md)  
- Tekniikka: [Osa 3 — Migraatio](03-MIGRATION-GUIDE.md)  
- Hakemisto: [fdocs/README.md](README.md)
