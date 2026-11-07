# ADDENDUM-0002 – MagiCAD, lämpöhäviöt ja ilmavirrat

- **Lähde:** projektin omistaja, keskustelu 2026-11-07. Kirjattu sisältö on omistajan ilmoittamaa.
  Agentin tulkinnat ja ehdotukset on merkitty erikseen (**Ehdotus**).
- **Suhde:** täydentää `CODEX_START.md`:tä ja ADDENDUM-0001:tä. Ristiriitatilanteessa tämä addendum on voimassa,
  kun projektin omistaja on hyväksynyt ehdotetut kohdat (ADR-0004, ADR-0005).
- **Päivitetty:** 2026-11-07, omistajan vastaukset §8.

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

## 8. Omistajan vastaukset 2026-11-07 (täydennys)

### 8.1 Ilmavirtojen lähdeohjeet

| Ohje | Julkaisija | Päiväys | Perusta |
|---|---|---|---|
| Opas asuinrakennusten ilmanvaihdon mitoitukseen | FINVAC ry (SuLVI, VSF, Sisäilmayhdistys, LIY) | 30.11.2017 | YM:n asetusluonnos 16.2.2017 |
| Opas ilmanvaihdon mitoitukseen muissa kuin asuinrakennuksissa | FINVAC ry + RTY, Talteka | 30.11.2019 | YM:n asetus 1009/2017 |

Lähde: talotekniikkainfo.fi (omistajan antamat linkit). Ohjeita ei tallenneta repositorioon (tekijänoikeus).
Agentti on lukenut molemmat. Havaintoja, jotka vaikuttavat tietomalliin (CALC-001):
- Ilmavirran peruste vaihtelee: per henkilö (dm³/s,hlö), per pinta-ala (dm³/s,m²), per huone tai asunto
  (dm³/s), per laite (WC-istuin, suihku), per paikka (katsomo, luentosali) ja ilmanvaihtokerroin (1/h, porrashuone).
  → Sääntötaulukon on tuettava useita perusteita samalle tilatyypille.
- Muissa kuin asuinrakennuksissa: *"Ulkoilmavirta määräytyy ensisijaisesti henkilöperusteen mukaan. Jos
  henkilömäärää ei ole suunnitteluvaiheessa luotettavasti määritettävissä, käytetään huonekohtaista,
  pinta-alaan, laitteiden tai kalusteiden määrään perustuvaa mitoitusta"* ja *"Ulkoilmavirta mitoitetaan
  suurimpaan ilmavirtaan johtavan kriteerin mukaan"* (opas 2019, luvut 1 ja 3).
- Asuinrakennuksissa mitoitus on **asuntotasoinen**: koko asunnon vähimmäisilmavirta (pinta-ala-, huonemäärä-
  ja vähimmäisehdot sekä saunan lisäys) jaetaan huoneisiin, ja huonekohtaisia arvoja suurennetaan tasapainon
  saavuttamiseksi (opas 2017, luvut 2–3). → Huonetason sääntö ei yksin riitä; tarvitaan asuntotaso.
- Asuinrakennusopas 2017 perustuu asetusluonnokseen. Muiden rakennusten opas (2019) viittaa
  asuinrakennusoppaan **vuoden 2019** versioon. → Avoin kysymys 1.
- **S1/S2/S3-luokkia ei ole näissä oppaissa.** Ne ovat Sisäilmastoluokitus 2018:sta (Sisäilmayhdistys). → Avoin kysymys 2.

### 8.2 Ilmavirran valintasääntö (omistaja)

1. Valitaan aina **suurin** ilmavirta: jos ohjeen ilmavirta on pienempi kuin valitun S-luokan, käytetään S-luokan arvoa.
2. Jos S-luokassa on sekä pinta-ala- että henkilöperuste: tarkistetaan arkkitehtikuvasta, onko henkilömäärä
   merkitty. Jos ei ole, mitoitetaan pinta-alan mukaan. Jos on, lasketaan molemmat ja valitaan suurempi.
3. Sisäilmastoluokka valitaan **projektikohtaisesti**.
4. Kaikki valinnat ja tulokset ovat asiantuntijan muutettavissa.

**Ehdotus:** tulos näyttää jokaisen tarkastellun perusteen arvon (ohje/pinta-ala, ohje/henkilö, S-luokka/pinta-ala,
S-luokka/henkilö ym.) ja merkitsee, mikä niistä on mitoittava. Henkilömäärän lähde on `model` (luettu kuvasta),
`expert` tai puuttuva. Tekoälyn tulkitsema henkilömäärä on `ai_estimate` (ADR-0005).

### 8.3 Mitoitusolosuhteet ja rakenteet (omistaja)

| Suure | Oletus | Muunneltavuus |
|---|---|---|
| Ulkoilman mitoituslämpötila | **−26 °C** | Muunneltava. **Kysytään aina** projektin alussa |
| U-arvot | Uudisrakennukselle tyypilliset | Muunneltava (projekti, rakennetyyppi, yksittäinen rakenne) |
| Vuotoilma, nurkkahuone ulkovaipalla | **0,1** | Muunneltava |
| Vuotoilma, ulkovaipan keskiosan huone | **0,05** | Muunneltava |
| Vuotoilma, rakennuksen keskellä oleva huone | **0** | Muunneltava |
| Sisälämpötila, kylpyhuone | **+21 °C** | Muunneltava |
| Sisälämpötila, sauna | **+21 °C** | Muunneltava |
| Sisälämpötila, tekniset tilat | **+18 °C** | Muunneltava |

**Ehdotukset, jotka omistajan pitää vahvistaa:**
- "Kysytään aina": laskenta ei käynnisty ennen kuin käyttäjä on vahvistanut ulkolämpötilan projektille.
  Vahvistus tallennetaan (kuka, milloin, arvo). Oletus −26 °C esitäytetään, mutta sitä ei hyväksytä hiljaisesti.
- Vuotoilman **yksikön** tulkinta on ilmanvaihtokerroin **1/h** (huoneen tilavuudesta). Vahvistettava.
- Huoneen sijainnin luokittelu deterministisesti geometriasta:
  *nurkkahuone* = ulkoseiniä vähintään kahdessa eri suunnassa; *ulkovaipan keskiosa* = ulkoseinää yhdessä
  suunnassa; *keskellä* = ei ulkoseinää. Luokka näytetään käyttäjälle, ja sen voi ohittaa.
- "Uudisrakennukselle tyypilliset U-arvot": agentti ei kirjoita arvoja muistinvaraisesti. Omistaja toimittaa
  arvot ja niiden lähteen (esim. energiatehokkuusasetuksen vertailuarvot, jos niitä tarkoitetaan).

## 9. Avoimet kysymykset omistajalle

1. Käytetäänkö asuinrakennuksille FINVACin 2017-oppaan ohella tai sijaan sen 2019-versiota?
2. Sisäilmastoluokitus 2018: saako agentti hakea julkaisun (sisailmayhdistys.fi), vai toimitatko S1/S2/S3-ilmavirtataulukot?
3. Mitkä ovat "uudisrakennukselle tyypilliset" U-arvot rakenteittain (ulkoseinä, yläpohja, alapohja/maanvarainen, ikkuna, ulko-ovi) ja niiden lähde?
4. Onko vuotoilman yksikkö 1/h, ja lasketaanko se huoneen nettotilavuudesta?
5. Lasketaanko maanvastaisen alapohjan lämpöhäviö erillisellä menetelmällä (maan lämpötila), ja millä oletuksilla?
6. Voiko MagiCAD Roomin tuloksia käyttää vertailuaineistona, ja millaisista kohteista?

## 10. Aiemmat avoimet kysymykset (vastattu)

Vastaukset §8:ssa. Alkuperäiset kysymykset säilytetään jäljitettävyyden vuoksi:

1. Talotekniikka-Infon ohjeet → §8.1
2. Sisäilmastoluokka projektikohtainen vai tilakohtainen → projektikohtainen (§8.2)
3. Laskentamenetelmä ja ulkolämpötila → −26 °C oletus (§8.3); menetelmä edelleen avoin
4. Vuotoilma → §8.3
5. Muiden tilatyyppien sisälämpötilat → §8.3
6. MagiCAD Room vertailuaineistona → edelleen avoin (§9 kysymys 6)
