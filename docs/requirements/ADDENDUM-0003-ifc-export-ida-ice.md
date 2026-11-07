# ADDENDUM-0003 – Lämpöhäviömallin IFC-vienti IDA ICE -simulointiin

- **Lähde:** projektin omistaja, 2026-11-07. Omistajan ilmoitukset on kirjattu sellaisinaan, agentin
  ehdotukset on merkitty (**Ehdotus**).
- **Suhde:** täydentää ADDENDUM-0001:tä ja -0002:ta. Päätösehdotus: [ADR-0006](../decisions/ADR-0006-ifc-export.md).

## 1. Tarve (omistaja)

- Lämpöhäviölaskentamallista on voitava viedä rakennuksen **3D IFC -malli**.
- Mallia käytetään **IDA ICE** -energiasimuloinnissa.
- IFC-mallissa on näyttävä ainakin **seinät, ikkunat ja tilaobjektit** sekä kaikki muu, mitä laskentamallissa
  on määritelty.

## 2. IDA ICE:n IFC-tuki (lähteet)

| Havainto | Lähde | Taso |
|---|---|---|
| IDA ICE 5.0: "Import from IFC4" | EQUA, IDA ICE 5.0 changelog | [L] |
| IDA ICE 5.1.1: "Better support for IFC4"; uusin versio 5.1.1.1 (marraskuu 2025) | EQUA, IDA ICE 5.1.1 changelog ja info center | [L] |
| IDA ICE 4: tukee IFC2x, IFC2x2 ja IFC2x3; tuo seinien, ikkunoiden, ovien ja kattojen geometrian; **vaatii tilat (spaces) oikeilla korkeuksilla**; tiloista muodostetaan simulointivyöhykkeet | EQUA, *Import of IFC BIM models to IDA ICE 4* | [L], vanha versio |
| Tuettu on mikä tahansa CAD-työkalu, joka vie IFC:n tiloineen ja **tilarajoineen** (space boundaries) | EQUA, aiempien versioiden muutosloki | [L], vanha |

Tarkistettava omistajan IDA ICE -versiolla: mitkä IFC-oliot ja ominaisuudet tuonti oikeasti lukee
(geometria vs. ominaisuusjoukot, kuten U-arvot ja lämpötilat).

## 3. Vaikutus huonemalliin (**Ehdotus**)

IFC-vienti edellyttää, että huonemalli säilyttää **3D-geometrian ja rakenneosien suhteet**, ei vain laskennan
tuloksia. Tämä otetaan huomioon jo GEO-tehtävissä:

- Tilan raja on suljettu monikulmio tason korkeusasemassa, ja tilalla on korkeus. Nettotilavuus lasketaan samasta geometriasta.
- Rakennusosat (ulkoseinä, väliseinä, yläpohja, alapohja, ikkuna, ovi) ovat omia olioitaan: geometria,
  paksuus, U-arvo ja sen lähde.
- Ikkunat ja ovet kuuluvat isäntäseinään, ja niillä on sijainti ja koko.
- **Tilarajat** (space boundary): jokainen tilan rajapinta tietää, mihin rakennusosaan ja mille puolelle
  (ulkoilma, maa, toinen tila) se rajoittuu. Sama tieto tarvitaan lämpöhäviölaskennassa, joten rakenne on yhteinen.
- Osittain maanalaisen seinän maanalainen osuus säilyy seinäkohtaisena tietona.

## 4. IFC-viennin sisältö (**Ehdotus**, vahvistettava)

| Laskentamallissa | IFC4-olio |
|---|---|
| Rakennus, kerrokset | `IfcBuilding`, `IfcBuildingStorey` |
| Tila | `IfcSpace` (suljettu raja + korkeus), nimi ja numero |
| Ulko- ja väliseinät | `IfcWall` |
| Ikkunat, ovet | `IfcWindow`, `IfcDoor` aukkoineen (`IfcOpeningElement`) |
| Ylä- ja alapohja | `IfcSlab` / `IfcRoof` |
| Tilan rajapinnat | `IfcRelSpaceBoundary` (fyysinen/virtuaalinen, sisäinen/ulkoinen) |
| U-arvot | `ThermalTransmittance` rakennusosan yleisessä ominaisuusjoukossa (esim. `Pset_WallCommon`) |
| Mitoitusarvot (sisälämpötila, ilmavirrat, lämpöhäviö) | standardin mukaiset tilan ominaisuusjoukot, kun sopivat löytyvät, muuten oma `Pset_Solmu_*` |

Ominaisuusjoukkojen nimet tarkistetaan IFC4-dokumentaatiosta ennen toteutusta.

## 5. Avoimet kysymykset omistajalle

1. Mikä IDA ICE -versio on käytössä? Riittääkö IFC4, vai tarvitaanko myös IFC2x3?
2. Tarkoititko "RUU-mallilla" huonemallia, vai onko se oma termi tai ohjelma?
3. Lukeeko IDA ICE teidän työnkulussanne IFC:stä vain geometrian, vai myös U-arvot, lämpötilat ja ilmavirrat?
   Vai syötetäänkö ne IDA:ssa erikseen?
4. Voitko testata vientiä omalla IDA ICE:lläsi, kun ensimmäinen versio on valmis (synteettinen esimerkkirakennus)?
5. Pitääkö viennin toimia myös DXF-lähtöisestä mallista, jossa Revit-mallia ei ole?
   (Vaikuttaa ADR-0006:n vaihtoehtoon.)
