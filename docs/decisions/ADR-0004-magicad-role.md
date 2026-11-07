# ADR-0004: MagiCAD for Revitin rooli

- **Tila:** Proposed
- **Päivämäärä:** 2026-11-07
- **Päättäjä:** Projektin omistaja
- **Liittyy:** ADDENDUM-0002, ADR-0002, roadmap (ROOM-, MAG-tehtävät), FR-HTG-002, FR-HTG-003

## Konteksti

Projektin omistaja käyttää MagiCAD for Revitiä. Siinä ovat Suomen tuotteiden tuotekirjastot, ja sillä
mitoitetaan patterit ja putkisto. Lämpöhäviöt lasketaan nyt MagiCAD Roomilla. Tavoitteena on laskea ne
tässä järjestelmässä (ADDENDUM-0002).

Lähteistä tiedetään [L]:
- MagiCAD 2027 for Revit tukee Revit 2027:ää ja kahta edellistä versiota.
- MagiCAD valitsee patterin tilan lämmitystehon tarpeen perusteella ja mitoittaa ne uudelleen, kun tarve muuttuu.
- Versiosta 2026 UR-2 alkaen on ulkoinen rajapinta tuotedatan lukemiseen ja kirjoittamiseen MagiCADin
  datasetin ja muiden sovellusten välillä. Dokumentaatio tulee asennuksen mukana. Tekniikka ja ominaisuudet ovat tuntemattomia.
- MagiCAD Roomin huonekohtainen tehontarvelaskenta näyttää olevan AutoCAD- ja BricsCAD-tuote, ei osa Revit-versiota.

## Päätösehdotus

1. **MagiCAD on tuotekirjaston ja patterien ja putkiston mitoituksen auktoriteetti.** Järjestelmä ei
   ylläpidä omaa patteriperherekisteriä, eikä se laske patterin tehoa tai kokoa itse.
2. **Järjestelmä laskee lämpöhäviön ja lämmitystehon tarpeen** (CALC-006, CALC-007) ja kirjoittaa tehon
   tarpeen tilan (Space) parametriin, jota MagiCAD käyttää. Kirjoitus on Revit-mallin muutos, joten se
   vaatii käyttäjän hyväksynnän ja tarkastuksen (`Applied` ≠ `Verified`).
3. **Patterien sijoitusehdotukset** ovat järjestelmän tehtävä. Vientitapa malliin ratkaistaan MAG-001:ssä.
   Siihen asti sijoitus viedään malliin MagiCADin omalla työkalulla käyttäjän toimesta.
4. Järjestelmä lukee MagiCAD-tuotteiden tietoja vain dokumentoitujen parametrien tai MagiCADin
   rajapinnan kautta. MagiCADin sisäistä tallennusmuotoa ei käytetä dokumentoimattomasti.
5. MagiCADin tuotedataa ei lähetetä ulkoiseen AI-palveluun, ellei MagiCADin käyttöehdot ja projektin
   aineistokäytäntö sitä salli.

## Avoimet asiat

- Minkä tilan parametrin MagiCAD lukee lämmitystehon tarpeeksi? (testiprotokolla M3)
- Mitä MagiCADin rajapinta osaa: tuotteen sijoitus, mitoituksen käynnistys, vain datan luku ja kirjoitus? (MAG-001)
- Toimivatko Solmu-lisäosa ja MagiCAD samassa Revit-prosessissa ilman riippuvuusristiriitoja? (M1)

## Seuraukset

**Positiiviset**
- Validoitu tuotekirjasto ja mitoitus. Niitä ei toteuteta eikä ylläpidetä itse.
- Järjestelmä keskittyy siihen, mitä MagiCAD for Revit ei tee: tunnistus, lämpöhäviöt, ilmavirrat,
  sijoitusehdotukset, hyväksyntä ja audit.

**Negatiiviset / riskit**
- Riippuvuus MagiCADin versioista, lisensseistä ja rajapinnan kehityksestä.
- Jos MagiCAD-tuotteen luonti ei onnistu ohjelmallisesti, sijoituksen vienti jää osin käsityöksi.
- Järjestelmän käyttö vaatii MagiCAD-lisenssin mitoitusvaiheessa.

## Vaihtoehdot

| Vaihtoehto | Arvio |
|---|---|
| Oma patterirekisteri ja oma mitoitus | Ei ehdoteta: päällekkäistä MagiCADin kanssa, eikä Suomen tuotekirjastoja ole saatavilla |
| **MagiCAD tuotteille ja mitoitukselle, järjestelmä lämpöhäviölle ja sijoitukselle** | **Ehdotettu** |
| Lämpöhäviötkin MagiCAD Roomissa | Ei ehdoteta: ristiriidassa omistajan tavoitteen kanssa (ADDENDUM-0002 §2) |
