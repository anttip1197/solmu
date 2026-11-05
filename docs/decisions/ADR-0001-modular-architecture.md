# ADR-0001: Modulaarinen monoliitti ja erillinen Python-palveluprosessi

- **Tila:** Proposed
- **Päivämäärä:** 2026-11-05
- **Päättäjä:** Projektin omistaja (odottaa hyväksyntää)
- **Liittyy:** CODEX_START.md §4–5, ADDENDUM-0001 §8, FND-002 (avoin)

## Konteksti

- Järjestelmä toimii Revit 2027:n yhteydessä, mutta valtaosa logiikasta (laskennat, validointi,
  AI-orkestrointi, DXF, datasetit, myöhemmin ML) on Revitistä riippumatonta.
- Kehitystiimi on yksi kehittäjä ja AI-agentit: hajautettu mikropalveluarkkitehtuuri olisi
  ylläpidollisesti raskas.
- Revitin ajoympäristö (Revit API, .NET, mahdollinen pyRevit) on rajoittunut ja vaikeasti testattava ilman Revit-asennusta.
- Revitistä riippumattomat testit on voitava ajaa ilman Revit-asennusta.

## Päätösehdotus

1. Python-osa toteutetaan **yhtenä modulaarisena monoliittina** (`heating_ai`), jonka moduulirajat
   noudattavat CODEX_START.md §5:n tavoiterakennetta.
2. Revit-integraatio on **erillinen komponentti erillisessä prosessissa** kuin Python-palvelu.
3. Prosessien välillä siirretään vain **versioituja, serialisoitavia ja validoituja tietosopimuksia**.
   Revit API -olioita ei siirretä.
4. Kerrosten riippuvuussuunta: `adapters` → `application` → `domain`. `domain` on puhdasta Pythonia
   ilman ulkoisia riippuvuuksia.
5. Moduulit luodaan asteittain vasta kun niille on sisältöä.

## Ei päätetä tässä ADR:ssä

- Revit-integraatiotekniikka (pyRevit vs. oma C#/.NET 10 -lisäosa) → FND-002 / tuleva ADR.
- Prosessien välinen viestintätekniikka (esim. named pipes, HTTP, stdio) → tuleva ADR.
- Tietosopimusten skeematekniikka ja mahdollinen validointikirjasto → FND-005.
- Tallennusratkaisu ja auditoinnin pysyvyys.

## Seuraukset

**Positiiviset**
- Domain ja laskennat ovat testattavissa ilman Revitiä.
- Yksi koodikanta ja yksi julkaisuyksikkö Python-puolella.
- Revitin versiopäivitykset rajautuvat adapteriin.

**Negatiiviset / riskit**
- Prosessiraja lisää serialisoinnin, versioinnin ja virheenkäsittelyn työtä.
- Kahden prosessin elinkaaren hallinta (käynnistys, aikakatkaisut, uudelleenyritykset) on suunniteltava.
- Jos FND-002 osoittaa prosessirajan epäkäytännölliseksi, tämä ADR on arvioitava uudelleen.

## Vaihtoehdot

| Vaihtoehto | Arvio |
|---|---|
| Kaikki logiikka Revit-lisäosan sisällä | Hylätty ehdotuksena: testattavuus ilman Revitiä heikko, sitoo logiikan Revitin ajoympäristöön |
| Mikropalvelut | Hylätty ehdotuksena: liian raskas yhden kehittäjän tiimille |
| Modulaarinen monoliitti + erillinen Revit-prosessi | **Ehdotettu** |
