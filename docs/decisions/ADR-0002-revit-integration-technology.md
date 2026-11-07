# ADR-0002: Revit 2027 -integraatiotekniikka

- **Tila:** Proposed – odottaa Revit 2027 -spike-ajoa ja projektin omistajan hyväksyntää
- **Päivämäärä:** 2026-11-07
- **Päättäjä:** Projektin omistaja
- **Liittyy:** FND-002, CODEX_START §8, ADR-0001, ADR-0003, FR-REV-001…006

## Konteksti

Revit-integraation tekniikkaa ei saa lukita ennen yhteensopivuustestiä (CODEX_START §8), ja tuotantoon
valitaan yksi ratkaisu. Selvitys: [FND-002](../research/FND-002-revit-2027-compatibility.md).

Keskeiset havainnot:
- Revit 2027 -lisäosat ovat .NET 10 -lisäosia; manifestin sijainti ja allekirjoituskäytäntö muuttuivat. [L]
- pyRevit tukee Revit 2027:ää versiosta 7.0, mutta tukeen on liittynyt asennusongelmia. [L]
  Sen Python-moottorit ovat IronPython 2.7.12 (oletus), IronPython 3.4.2 ja kokeellinen CPython 3.12.3. [V]
- Projektin domain-koodi vaatii Python ≥ 3.11, joten sitä ei voi ajaa pyRevitin IronPythonilla. [V]
  Kummassakin vaihtoehdossa Revit-puoli on siis ohut adapteri, ja logiikka on erillisessä CPython-prosessissa.
- C#-spike-lisäosa kääntyy Revit 2027.3 -referenssikirjastoja vasten, ja sen IPC-kirjasto toimii
  CPython-palvelun kanssa ilman Revitiä. [V]

## Päätösehdotus

1. Tuotannon Revit-integraatio toteutetaan **omana C#/.NET 10 -lisäosana** (`net10.0-windows`, x64).
2. Lisäosa on **ohut adapteri**: lukeminen, yksikkömuunnokset, serialisointi, hyväksyttyjen muutosten
   transaktiot ja toteutuksen tarkastus. Ei suunnittelu-, laskenta- tai AI-logiikkaa.
3. **pyRevitiä ei käytetä tuotannossa**, eikä rinnakkaista pyRevit-toteutusta rakenneta.
4. Lisäosa asennetaan kehityksessä per-user. Tuotannossa käytetään allekirjoitettua all-users-asennusta
   (`C:\Program Files\Autodesk\Revit\Addins\2027`). Allekirjoitusvarmenne on erillinen päätös.
5. Lisäosa käyttää omaa riippuvuuskontekstia (Revit 2027:n manifestiasetukset), jotta muiden lisäosien
   kirjastot eivät törmää. Toteutus FND-007:ssä spike-tulosten perusteella.

## Hyväksymisen edellytykset

ADR siirretään tilaan `Accepted` vain, jos [testiprotokollan](../testing/revit-2027-spike-protocol.md)
C#-osio on ajettu Revit 2027:ssä ja:
- lisäosa latautuu ja ajaa komennon ilman mallin muutoksia
- huoneiden, rajojen, ikkunoiden ja yksiköiden luku tuottaa raportin
- CPython-lapsiprosessin edestakainen viestintä onnistuu Revitistä käsin

Jos jokin näistä epäonnistuu, ADR päivitetään havaintojen mukaan ennen päätöstä.

## Seuraukset

**Positiiviset**
- Autodeskin virallinen ja dokumentoitu polku; ei riippuvuutta kolmannen osapuolen julkaisutahdista.
- Vahvasti tyypitetty prosessiraja: DTO-tyypit tarkistetaan käännösaikana.
- IPC ja serialisointi testattavissa ilman Revitiä (harness, CI).

**Negatiiviset / riskit**
- Kaksi kieltä (C# ja Python) yhden kehittäjän projektissa.
- Jokainen Revit-vuosiversio vaatii uudelleenkäännöksen ja testauksen.
- Tuotantoasennus vaatii koodin allekirjoitusvarmenteen.
- Kokeilusykli on hitaampi kuin pyRevitissä (Revit on käynnistettävä uudelleen lisäosan muutoksen jälkeen).

## Vaihtoehdot

| Vaihtoehto | Arvio |
|---|---|
| pyRevit (IronPython) tuotantoadapterina | Ei ehdoteta: kolmannen osapuolen riippuvuus, Revit 2027 -asennusongelmat [L], dynaaminen raja, IronPython ei aja domain-koodia [V] |
| pyRevit CPython 3.12 -moottori | Ei ehdoteta: merkitty kokeelliseksi (`runtime = false`) [V], vakausongelmia raportoitu [L] |
| Dynamo / PythonNet3 | Ei ehdoteta: skriptiympäristö, ei sovi lisäosan käyttöliittymään ja hyväksyntätyönkulkuun |
| **C#/.NET 10 -lisäosa + CPython-palvelu** | **Ehdotettu** |
