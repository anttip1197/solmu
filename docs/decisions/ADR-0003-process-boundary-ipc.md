# ADR-0003: Revit- ja Python-prosessien välinen viestintä

- **Tila:** Proposed – odottaa Revit 2027 -spike-ajoa ja projektin omistajan hyväksyntää
- **Päivämäärä:** 2026-11-07
- **Päättäjä:** Projektin omistaja
- **Liittyy:** FND-002, FND-003, FND-005, ADR-0001, ADR-0002, FR-REV-006

## Konteksti

Revit-lisäosa ja Python-palvelu ovat eri prosesseja (ADR-0001). Viestintätekniikkaa ei saa lukita
ilman perusteltua ADR:ää (CODEX_START §4). Vaatimukset:
- Vain paikallinen viestintä samalla koneella. Malliaineisto ei saa vuotaa verkkoon.
- Ei uusia ajonaikaisia riippuvuuksia ilman perustetta (Python-puolella vain standardikirjasto).
- Virheet eivät saa jäädä hiljaisiksi, eikä palvelun kaatuminen saa kaataa Revitiä.
- Testattavissa ilman Revitiä.

## Päätösehdotus

1. **Lisäosa käynnistää Python-palvelun lapsiprosessina** ja omistaa sen elinkaaren.
   Yksi palveluprosessi per Revit-istunto; palvelu sammuu, kun stdin suljetaan.
2. **Kehystys: yksi UTF-8 JSON-olio per rivi** stdinin ja stdoutin yli. stdout on varattu protokollalle;
   lokit kirjoitetaan stderriin tai tiedostoon (FND-006).
3. Jokaisessa viestissä on protokollan nimi, **versio** ja pyynnön tunniste. Vastaus sisältää saman
   tunnisteen sekä `ok`-tilan tai virhekoodin. Viestin enimmäiskoko on rajattu.
4. Asiakkaalla on aikakatkaisu jokaiselle pyynnölle. Aikakatkaisu tai kaatuminen raportoidaan käyttäjälle,
   eikä mallia muuteta.
5. Revit API -kutsut tehdään vain Revitin API-kontekstissa. Modeless-käyttöliittymästä kutsut ohjataan
   `ExternalEvent`-mallin kautta; taustasäie hoitaa vain IPC:n.
6. Varsinaiset viestisopimukset ja niiden skeemat määritellään FND-005:ssä. Spiken `solmu-spike`-protokolla
   ei ole tuotantosopimus.

## Näyttö

- [V] .NET 10 -asiakas ↔ CPython-palvelu Linuxissa: kaikki harness-tarkistukset läpi; 100 peräkkäistä
  pyyntöä noin 12 ms; 500 huoneen raportti noin 6 ms.
- [V] Python-palvelun virheenkäsittely: 16 automaattista testiä (`tests/integration/test_revit_spike_service.py`).
- [R] Sama Windowsissa Revit 2027:n prosessista: testiprotokollan kohdat C4 ja P4.

## Seuraukset

**Positiiviset**
- Ei portteja, palomuurikehotteita tai todennustunnisteita; muut prosessit eivät voi yhdistää.
- Python-puoli vain standardikirjastoa; testattavissa millä tahansa käyttöjärjestelmällä.
- Palvelun elinkaari on sidottu Revit-istuntoon: ei orpoja palveluja.

**Negatiiviset / riskit**
- Yksi asiakas per palveluprosessi. Jos tarvitaan pysyvä, usean Revit-istunnon jakama palvelu,
  tätä ADR:ää on arvioitava uudelleen (vaihtoehto: nimetyt putket).
- Pyyntö–vastaus-malli peräkkäin. Rinnakkaiset pyynnöt vaativat tunnistepohjaisen multipleksoinnin (tunniste on jo mukana).
- Palvelun käynnistysaika (Python + importit + virustorjunta) on mitattava Windowsissa.
- Python-ajoympäristön sijainti ja jakelu on ratkaistava (FND-003).

## Vaihtoehdot

| Vaihtoehto | Arvio |
|---|---|
| **stdio JSON-rivit, lapsiprosessi** | **Ehdotettu**: yksinkertaisin, paikallinen, ei riippuvuuksia |
| Nimetyt putket | Varavaihtoehto: tukee itsenäistä palvelua ja useita asiakkaita, mutta Python-palvelin vaatii `pywin32`:n tai yksityisen `_winapi`-rajapinnan |
| Localhost-HTTP/WebSocket | Ei ehdoteta v1:ksi: porttien hallinta ja todennus tarvitaan, koska muut paikalliset prosessit voivat yhdistää |
| gRPC | Ei ehdoteta: raskaat riippuvuudet molemmin puolin |
| Revit API -olioiden suora jakaminen (pythonnet samassa prosessissa) | Hylätty ehdotuksena: rikkoo ADR-0001:n prosessirajan |
