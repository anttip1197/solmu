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

## 5. Omistajan vastaukset 2026-11-07

1. Skeema: **IFC4**.
2. "RUU-malli" tarkoitti **room-mallin IFC:tä** (huonemallista vietävää IFC:tä).
3. IDA ICE:hen tuodaan **geometria ja tilat**. Omistaja pyysi varmistamaan, tuleeko muita tietoja (§6).
4. DXF-kysymys jäi epäselväksi, ja se kysytään uudelleen (§8).
5. Omistaja **testaa viennin omalla IDA ICE:llään**.

## 6. Mitä IDA ICE lukee IFC:stä (EQUAn ajantasainen ohje)

Lähde: EQUA, IDA ICE Getting started: *IFC Objects and IFC Geometries* (2025-04-26) ja *IFC in IDA ICE*, sekä
IDA ICE Help: *Options for IFC import*, *IFC mapping* (equa.cloud.xwiki.com, luettu 2026-11-07).

| IFC-olio | IDA ICE:n tuomat ominaisuudet |
|---|---|
| `IfcSpace` | Tilan nimi (geometria prismana, vakiokorkeus) |
| `IfcWall` | Rakennetyyppi (construction type), ulko-/sisäseinäluokitus |
| `IfcWindow` | Rakennetyyppi |
| `IfcSlab` | Rakennetyyppi |
| `IfcDoor` | Geometria (rajoitettu ominaisuustuki) |
| `IfcCurtainWall` | Yksinkertaistettu geometria |

**Johtopäätös:** IDA ICE **ei tuo IFC:stä U-arvoja, lämpötiloja eikä ilmavirtoja**. Rakennetyypit yhdistetään
IDA:n omiin rakenteisiin IDA:n mapping-työkalulla, ja vyöhykkeiden lämpötilat ja ilmavirrat tulevat IDA:n
vyöhykepohjista. Ohjeen mukaan selkeät ja johdonmukaiset rakennetyyppien nimet nopeuttavat mallin valmistelua.

### IFC-tiedoston vaatimukset IDA ICE -tuontia varten (EQUAn ohjeesta)

- Yksiköt määritelty (muunnetaan SI-yksiköiksi). Kerrosten korkeusasemat annettu.
- Jokainen elementti kuuluu **yhteen kerrokseen**, eikä seinä jatku kerroksesta toiseen.
- Tiloilla on **selkeä nimi**. Tilat ovat prismoja vakiokorkeudella, eivätkä ne leikkaa toisiaan (leikkaavista tiloista suurempi poistetaan oletuksena).
- Kerroksen ulkoraja saadaan joko **kerroksen kattavasta "gross space" -tilasta** (oletusasetus) tai ulkoseinistä.
  Siksi seinät luokitellaan **ulko- tai sisäseiniksi**.
- Seinät ovat pystysuoria, vakiopaksuisia ja niillä on keskiviiva-akseli. Seinillä, laatoilla ja ikkunoilla on **rakennetyyppi**.
- Ikkunat ja ovet ovat seinän **aukossa** (opening), ja aukon koordinaatisto vastaa seinää. Aukko on kokonaan seinän sisällä.
  Erillisiä ikkunoita ei tueta.
- Katto kattaa kaikki ylimmät kerrokset.

## 7. Tarkennettu vienti (**Ehdotus**)

- Vienti noudattaa §6:n vaatimuksia. Viennin jälkeen ajetaan oma tarkistus, joka testaa ne ennen kuin tiedosto annetaan käyttäjälle.
- **Rakennetyyppien nimet** muodostetaan laskentamallin rakenteista johdonmukaisesti, esim. `US1 Ulkoseinä U=0,17`,
  jotta IDA:n mapping on helppo tehdä. Sama rakenne saa aina saman nimen.
- `IfcSpace`: `Name` = huonenumero, `LongName` = huoneen nimi. Kerroskohtainen gross space lisätään, jos testi IDA ICE:ssä
  osoittaa sen hyödylliseksi.
- U-arvot ja mitoitusarvot voidaan silti viedä ominaisuusjoukkoina muita ohjelmia varten. IDA ICE ei niitä lue.
- **Lisäehdotus:** vienti tuottaa IFC:n rinnalle **vyöhyketaulukon** (tilat, sisälämpötilat, ilmavirrat, rakennetyypit
  U-arvoineen), jonka avulla arvot on helppo syöttää IDA:n vyöhykepohjiin ja rakenteisiin. Omistaja päättää, tarvitaanko sitä.

## 8. Avoimet kysymykset omistajalle

1. Tarvitaanko vyöhyketaulukko (§7)? Missä muodossa: Excel vai CSV?
2. (Uudelleen, selkeämmin) Luetaanko lähtötiedot aina Revitistä, vai tuleeko joskus pelkkä arkkitehdin DXF-pohjapiirustus
   ilman Revit-mallia? Jos jälkimmäinen, IFC on muodostettava kokonaan meidän huonemallistamme. ADR-0006 ehdottaa
   tätä joka tapauksessa.
