# ADDENDUM-0002 – MagiCAD, lämpöhäviöt ja ilmavirrat

- **Lähde:** projektin omistaja, keskustelu 2026-11-07. Kirjattu sisältö on omistajan ilmoittamaa.
  Agentin tulkinnat ja ehdotukset on merkitty erikseen (**Ehdotus**).
- **Suhde:** täydentää `CODEX_START.md`:tä ja ADDENDUM-0001:tä. Ristiriitatilanteessa tämä addendum on voimassa,
  kun projektin omistaja on hyväksynyt ehdotetut kohdat (ADR-0004, ADR-0005).

## 1. Nykyinen työnkulku (omistajan ilmoitus)

- Suunnittelussa käytetään **MagiCAD for Revit** -laajennusta. Siinä ovat Suomen tuotteiden tuotekirjastot,
  ja patterien ja putkiston mitoitus tehdään sillä.
- Lämpöhäviöt lasketaan nykyisin **MagiCAD Room** -sovelluksella.

## 2. Tavoite (omistajan ilmoitus)

- Lämpöhäviöt lasketaan **tässä järjestelmässä**, ei MagiCAD Roomissa.
- Tekoäly tai koneoppimismalli tunnistaa ulkovaipan rajat, huoneet ja tilat sekä ikkunat.
- Tiloille määritetään ilmavirrat. Koneoppimismalli voi tuottaa ilmamäärän (ks. §5).

## 3. Mitoitusolosuhteet (omistajan ilmoittamat projektin oletusarvot)

| Suure | Oletusarvo | Huomio |
|---|---|---|
| Tuloilman lämpötila talvimitoitusolosuhteissa | **+18 °C** | Tuloilma puhalletaan alilämpöisenä |
| Sisälämpötila, normaalit oleskelutilat | **+21 °C** | |
| Sisälämpötila, porrashuoneet ja varastot | **+18 °C** | "yleensä tyypillisesti" |

- Arvot ovat **projektin oletusarvoja, joiden lähde on projektin omistaja**. Niitä ei esitetä säädösvaatimuksina.
- **Asiantuntija voi muuttaa** arvoja jälkikäteen projekti- ja tilakohtaisesti laskennan tarkentamiseksi.
  Jokainen muutos tallennetaan: kuka, milloin, vanha ja uusi arvo, perustelu.
- Laskentatulos kertoo aina, mitä arvoja käytettiin ja mistä ne tulivat (oletus vai asiantuntijan muutos).
- Tilan sisälämpötilan oletus valitaan tilan käyttötarkoitusluokasta. Luokittelu on CALC-002:n tehtävä.

**Ehdotus (laskennan rakenne):** tuloilman ilmanvaihtolämpöhäviö lasketaan tilan sisälämpötilan ja
tuloilman lämpötilan erotuksesta (normaalitilassa 21 − 18 = 3 K), ei ulkolämpötilasta. Tarkka kaava,
menetelmä (esim. SFS-EN 12831-1 ja kansalliset liitteet), ulkoilman mitoituslämpötilat ja niiden
lähteet sekä versiot **dokumentoidaan ja omistaja hyväksyy ne ennen CALC-006:n toteutusta**.

## 4. Ilmavirtojen mitoitus (omistajan ilmoitus)

- Ilmamäärät mitoitetaan **Talotekniikka-Infon ohjeistuksilla**.
- Ilmamääriin voi vaikuttaa **sisäilmastoluokka S1, S2 tai S3**.

**Ehdotus:**
- Sisäilmastoluokka on projektitason asetus, jonka voi ohittaa tilakohtaisesti.
- Mitoitussäännöt (tilatyyppi × sisäilmastoluokka → ilmavirta) tallennetaan **versioituna sääntötaulukkona**,
  johon on merkitty lähde (ohjeen nimi, versio, päivämäärä, kohta).
- Agentti ei kirjoita taulukon lukuarvoja muistinvaraisesti. Omistaja toimittaa ohjeet tai taulukon,
  ja jokainen arvo tarkistetaan lähdettä vasten. Ohjeiden tekijänoikeudet huomioidaan: repositorioon
  tallennetaan vain tarvittavat lukuarvot lähdeviitteineen, ei ohjeiden tekstiä.

## 5. Koneoppimisen ja tekoälyn rooli insinööriarvoissa

Omistajan tavoite on, että ML voi tuottaa ilmamäärän. ADDENDUM-0001 §5 kieltää ilmavirtojen keksimisen.
**Ehdotettu sovitus (ADR-0005):**

1. ML/AI **tunnistaa** geometrian: ulkovaippa, huoneet, tilat, ikkunat ja tilan käyttötarkoitus.
2. **Deterministinen sääntömoottori** laskee ilmavirran tilatyypistä, sisäilmastoluokasta ja geometriasta.
3. ML saa **ehdottaa** ilmavirtaa. Ehdotus näytetään säännön arvon rinnalla, ja se merkitään arvioksi
   (malli, malliversio, luottamus).
4. Laskennassa käytetään vain arvoa, jonka lähde on sääntö tai asiantuntijan hyväksyntä.
   ML-arvo ei koskaan siirry laskentaan hiljaisesti.
5. Jos sääntö puuttuu (tuntematon tilatyyppi), tilan laskenta jää tilaan "syötteet puutteelliset".

## 6. MagiCADin rooli

**Ehdotus (ADR-0004):**
- MagiCAD on **tuotekirjaston ja patterien ja putkiston mitoituksen** auktoriteetti. Emme rakenna omaa patterirekisteriä.
- Järjestelmä tuottaa tilakohtaisen lämpöhäviön ja lämmitystehon tarpeen ja **vie sen MagiCADin käyttämään
  tilan (Space) parametriin**. MagiCAD mitoittaa patterit sen perusteella. Parametri selvitetään spike-ajossa
  (testiprotokolla M3).
- Patterien sijoitusehdotukset ovat järjestelmän tehtävä. Tapa, jolla patteri viedään malliin MagiCAD-tuotteena,
  on avoin (MagiCADin oma työkalu, MagiCADin rajapinta versiosta 2026 UR-2 lähtien, tai Revit API + MagiCADin
  uudelleenmitoitus). Ratkaistaan erillisessä selvityksessä (MAG-001).

## 7. Validointi MagiCAD Roomia vasten

**Ehdotus:** koska lämpöhäviöt lasketaan nyt MagiCAD Roomilla, sen tulokset ovat luonteva
**vertailuaineisto**. CALC-008 vertaa järjestelmän tuloksia MagiCAD Roomin tuloksiin samoilla
syötteillä valituissa testikohteissa. Poikkeamat raportoidaan osatekijöittäin (seinät, ikkunat,
ilmanvaihto ym.). Vertailuaineiston käyttöoikeus ja säilytys dokumentoidaan (AGENTS.md §7).

## 8. Avoimet kysymykset omistajalle

1. Mitä Talotekniikka-Infon ohjeita ja mitä versioita ilmamäärien mitoitukseen käytetään?
2. Määräytyykö sisäilmastoluokka projektikohtaisesti, vai voiko se vaihdella tiloittain?
3. Mitä laskentamenetelmää ja mitoittavaa ulkolämpötilaa MagiCAD Roomissa nyt käytetään?
4. Lasketaanko vuotoilma (infiltraatio) erikseen? Millä oletuksilla?
5. Mitkä muut tilatyypit kuin oleskelutilat, porrashuoneet ja varastot tarvitsevat oman sisälämpötilan
   (esim. kylpyhuoneet, saunat, tekniset tilat)?
6. Voiko MagiCAD Roomin tuloksia käyttää vertailuaineistona, ja millaisista kohteista?
