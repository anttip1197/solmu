# ADR-0006: IFC-vienti lämpöhäviömallista

- **Tila:** Proposed
- **Päivämäärä:** 2026-11-07
- **Päättäjä:** Projektin omistaja
- **Liittyy:** ADDENDUM-0003, ADR-0001, ADR-0004, GEO-tehtävät, FR-IFC-001…005 (ehdotettu etuliite)

## Konteksti

Lämpöhäviömallista viedään 3D IFC -malli IDA ICE -simulointiin (ADDENDUM-0003). IDA ICE 5.x tuo IFC4:ää,
ja simulointivyöhykkeet muodostetaan tiloista ja tilarajoista [L]. Huonemalli voi olla peräisin Revitistä
tai DXF:stä (ADDENDUM-0001), ja asiantuntija voi muuttaa sen arvoja (U-arvot, maanalainen osuus, lämpötilat).

## Päätösehdotus

1. IFC muodostetaan **järjestelmän omasta huonemallista** Python-palvelussa, ei Revitin IFC-viennillä.
   Perusteet: vientiin tulevat myös asiantuntijan muutokset, ja vienti toimii myös DXF-lähtöisille malleille.
2. Ensisijainen skeema on **IFC4**. IFC2x3 lisätään vain, jos omistajan IDA ICE -versio sitä vaatii.
3. Toteutukseen käytetään **IfcOpenShell**-kirjastoa (Python, LGPL-3.0). Se on ensimmäinen ajonaikainen
   riippuvuus, joten se perustellaan erikseen. IFC:n (STEP) kirjoittaminen käsin olisi virhealtista, ja
   kirjasto osaa myös validoida tuotoksen. Lisenssin soveltuvuus tarkistetaan ennen käyttöönottoa.
4. Vienti on oma moduulinsa (esim. `heating_ai.adapters.ifc`). Domain ei riipu IFC:stä.
5. Hyväksymistesti: vientiä ajetaan synteettisellä rakennuksella, tuotos validoidaan IFC-skeemaa vasten ja
   tuodaan omistajan IDA ICE:en. Tuonnin tulos dokumentoidaan.

## Vaihtoehdot

| Vaihtoehto | Arvio |
|---|---|
| Revitin oma IFC-vienti (tilat ja tilarajat) | Ei sisällä asiantuntijan muutoksia, ei toimi DXF-lähtöisille malleille. Voi toimia vertailuna |
| MagiCADin IFC-vientirajapinta (2027) | Vie MagiCAD-mallin, ei lämpöhäviömallia. Selvitetään MAG-001:ssä |
| IFC:n kirjoittaminen ilman kirjastoa | Ei ehdoteta: suuri virheriski, ei validointia |
| **Oma vienti huonemallista, IfcOpenShell, IFC4** | **Ehdotettu** |

## Seuraukset

- GEO-tehtävien huonemallin on säilytettävä 3D-geometria, rakennusosat ja tilarajat (ADDENDUM-0003 §3).
- Ensimmäinen ajonaikainen riippuvuus. Sen versio lukitaan ja lisenssi dokumentoidaan.
- IDA ICE -yhteensopivuutta ei voi testata CI:ssä. Se testataan omistajan koneella kuten Revit-testit.
