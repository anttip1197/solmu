# FND-002 – Revit 2027 -yhteensopivuusselvitys

- **Tila:** Selvitys ja spike-toteutus valmiit. **Revit 2027 -ajo odottaa** (ks. [testiprotokolla](../testing/revit-2027-spike-protocol.md)).
- **Päivämäärä:** 2026-11-07
- **Johtopäätökset:** [ADR-0002](../decisions/ADR-0002-revit-integration-technology.md) ja
  [ADR-0003](../decisions/ADR-0003-process-boundary-ipc.md), molemmat tilassa `Proposed`.

## Näytön tasot

Jokaisella havainnolla on merkintä siitä, mihin se perustuu:

| Merkintä | Tarkoittaa |
|---|---|
| **[V]** | Varmennettu tässä ympäristössä (komento ajettu, tulos nähty). Ei Revitiä. |
| **[L]** | Lähteestä (julkaisutiedot, dokumentaatio, issue). Ei varmennettu itse. |
| **[R]** | Varmennettava Revit 2027:ssä spike-ajossa. Ei vielä tiedossa. |

Huom.: Autodeskin dokumentaatiosivut (help.autodesk.com, blog.autodesk.io, rvtdocs.com) eivät olleet
tämän kehitysympäristön verkossa sallittuja. [L]-havainnot perustuvat hakukoneiden tiivistelmiin näistä
lähteistä sekä GitHubiin. Ne on tarkistettava alkuperäisestä lähteestä ennen ADR:n hyväksymistä.

## 1. Revit 2027 ja .NET

| # | Havainto | Taso |
|---|---|---|
| 1.1 | Revit 2027:n lisäosat käännetään .NET 10:lle. Autodeskin migraatio-ohje: SDK 10.0.100, `global.json` tarvittaessa, pienet .NET 8 → 10 -muutokset. | [L] |
| 1.2 | All-users-manifestin sijainti muuttui: `C:\ProgramData\Autodesk\Revit\Addins\2027` → `C:\Program Files\Autodesk\Revit\Addins\2027`. Per-user `%APPDATA%\Autodesk\Revit\Addins\2027` on edelleen tuettu. | [L] |
| 1.3 | Yhteisöraporttien mukaan Revit 2027 hylkää allekirjoittamattomat lisäosat all-users-sijainnista; per-user toimii allekirjoittamattomana. | [L] (yhteisö) |
| 1.4 | Uudet manifestiasetukset riippuvuuksien eristykseen: `UseAllContextsForDependencyResolution`, `PublicAssemblies`, `Dependencies` (`ClientIdDependency`, `ContextNameDependency`). | [L] |
| 1.5 | Yhteisöraportti: Revit 2026:n assembly-deduplikointi puuttuu 2027:stä → tyyppi-identiteettiongelmia, jos samaa assemblya ladataan useaan kontekstiin. | [L] (yhteisö) |
| 1.6 | Kolmannen osapuolen raportti (AVAIL): .NET 10 poisti järjestelmäriippuvuuden, jota heidän prosessienvälinen drag-and-drop käytti. → IPC-tekniikka on testattava, ei oletettava. | [L] |
| 1.7 | `net10.0-windows` -lisäosa, joka käyttää `ElementId.Value`, `Room`, `GetBoundarySegments`, `FamilyInstance.get_FromRoom/ToRoom`, `UnitUtils.ConvertFromInternalUnits`, `UnitTypeId`, `SpecTypeId`, `FormatOptions.GetUnitTypeId`, kääntyy Revit 2027.3 -referenssikirjastoja vasten ilman varoituksia. | **[V]** |
| 1.8 | Lisäosan käyttäytyminen Revitissä (lataus, allekirjoituskehote, ajonaikaiset arvot). | [R] |

Referenssikirjastot: NuGet `Nice3point.Revit.Api.RevitAPI` / `RevitAPIUI` 2027.3.0 (kolmannen osapuolen
julkaisemat referenssipaketit; ei kopioida lisäosan tulosteeseen). [V] Paketit ovat saatavilla
(versiot 2027.0.0 … 2027.3.0).

## 2. pyRevit

| # | Havainto | Taso |
|---|---|---|
| 2.1 | pyRevit 7.0.0 (6.10.2026) ilmoittaa tukevansa Revit 2021–2027. | [L] |
| 2.2 | Revit 2027 -tukeen liittyi 2026 keväällä–kesällä asennusongelmia (manifestin polku, all-users vs. per-user, nauha ei näkynyt). Korjauksia versioissa 6.4.0 ja 6.5.0. Yksi kesäkuun 2026 raportti (nauha puuttuu per-user-asennuksessa) jäi issuessa ilman vastausta. | [L] |
| 2.3 | Kolmannen osapuolen ohje: koneella, jossa on vain Revit 2027:n mukana tuleva .NET 10, pyRevit-välilehti ei ilmesty ennen kuin .NET 8 asennetaan. Ei vahvistettu virallisesta lähteestä. | [L] (heikko) |
| 2.4 | pyRevitin moottorit (`pyRevitfile`, master): oletus **IronPython 2.7.12**, lisäksi **IronPython 3.4.2** ja **CPython 3.12.3** (`runtime = false`). | [V] (tiedosto luettu GitHubista) |
| 2.5 | pyRevitin oma dokumentaatio on aiemmin kuvannut CPython-moottoria kehitysvaiheessa olevaksi ja mahdollisesti epävakaaksi. | [L] |
| 2.6 | Projektin domain-koodi (`StrEnum`, `dataclass(slots=True)`, `X \| None`) vaatii Python ≥ 3.11. **Sitä ei voi ajaa IronPython 2.7:llä tai 3.4:llä.** | [V] (kielen versiovaatimus) |
| 2.7 | pyRevit-spike-skripti ajetaan Revitissä. | [R] |

Johtopäätös: pyRevitissä ajettava IronPython-koodi ei voi jakaa domain- ja laskentakoodia
Python-palvelun kanssa. pyRevit olisi joka tapauksessa vain ohut Revit-adapteri, jolloin sen etu
C#-lisäosaan nähden on lähinnä nopeampi kokeilusykli.

## 3. Dynamo

| # | Havainto | Taso |
|---|---|---|
| 3.1 | Revit 2027 sisältää Dynamo 4.x:n; oletus-Python on PythonNet3 (CPython 3.11 -pohjainen + Python.NET 3). | [L] |
| 3.2 | Dynamo on graafipohjainen skriptiympäristö, ei tuotantolisäosan käyttöliittymä- ja hyväksyntätyönkulkuun sopiva alusta. | Arvio |

Dynamo rajataan pois tuotantovaihtoehtona.

## 4. Prosessien välinen viestintä

| # | Havainto | Taso |
|---|---|---|
| 4.1 | .NET 10 -asiakas voi käynnistää CPython-prosessin ja vaihtaa JSON-rivejä stdin/stdoutin yli: ping, 500 huoneen raportti, virheviesti, palvelu jatkaa virheen jälkeen, 100 peräkkäistä pyyntöä ~12 ms, puuttuva Python → hallittu poikkeus. (Linux, .NET 10.0.114 SDK, CPython 3.13.) | **[V]** |
| 4.2 | Python-palvelu: virheelliset viestit (JSON, protokolla, versio, tyyppi, payload, koko) palauttavat virhekoodin eivätkä kaada palvelua; stdout sisältää vain protokollaviestit; UTF-8 (ÄÖÅ) säilyy. | **[V]** (16 testiä) |
| 4.3 | Sama Windowsissa Revitin prosessista käynnistettynä (Windowsin konsolikoodisivu, virustorjunta, käynnistysaika). | [R] |
| 4.4 | Revit API -kutsut on tehtävä Revitin API-kontekstissa; modeless-käyttöliittymästä tämä vaatii `ExternalEvent`-mallin. Taustasäie ei saa kutsua Revit API:a. | [L] |
| 4.5 | Nimetyt putket (named pipes): Python-palvelin vaatisi `pywin32`:n tai yksityisen `_winapi`-rajapinnan; asiakkaana Python voi avata putken tiedostona. | Arvio (stdlibin tunnettu rajoite) |
| 4.6 | Localhost-HTTP: vaatii portin valinnan ja todennustunnisteen, koska muut paikalliset prosessit voivat yhdistää. | Arvio |

## 5. Vaihtoehtojen vertailu

| Kriteeri | A: pyRevit (IronPython) | B: C#/.NET 10 -lisäosa | C: Dynamo |
|---|---|---|---|
| Autodeskin tukema polku | Ei (kolmas osapuoli) | **Kyllä** | Kyllä, mutta skriptiympäristö |
| Revit 2027 -tuki tänään | Kyllä 7.0:sta, historiassa asennusongelmia [L] | Kyllä, käännös [V], ajo [R] | Kyllä [L] |
| Domain-koodin jakaminen | Ei (IronPython 2.7/3.4) [V] | Ei (eri kieli) | Osittain (CPython 3.11) |
| Riippuvuus ulkoisesta julkaisutahdista | Suuri | Pieni (vain Revit SDK) | Keskisuuri |
| Allekirjoitus ja käyttöönotto | pyRevitin asennus + oma laajennus | Oma allekirjoitus, all-users tai per-user | Dynamo-graafit |
| Tyypitetty prosessiraja | Heikko (dynaaminen) | **Vahva** (record-tyypit, käännösaikainen tarkistus) | Heikko |
| Kokeilusyklin nopeus | **Nopea** (ei käännöstä) | Hitaampi (käännös, Revitin uudelleenkäynnistys) | Nopea |
| Revit-vuosiversion päivitys | pyRevitin päivitys | Uudelleenkäännös uudella SDK:lla | Dynamo-versio |
| Testattavuus ilman Revitiä | Heikko | Hyvä (IPC-kirjasto ja harness ajettu [V]) | Heikko |

## 6. Suositus (ehdotus, ei päätös)

1. **Tuotannon Revit-integraatio: oma C#/.NET 10 -lisäosa (vaihtoehto B)** ohuena adapterina:
   lukee mallia, muuntaa yksiköt, serialisoi, toteuttaa hyväksytyt muutokset transaktioissa ja tarkastaa tuloksen.
2. **Kaikki sovelluslogiikka erillisessä CPython-palveluprosessissa** (ADR-0001).
3. **IPC v1: lisäosa käynnistää Python-palvelun lapsiprosessina, JSON-rivit stdin/stdoutin yli** (ADR-0003).
4. pyRevitiä ei käytetä tuotannossa. Sitä voi halutessa käyttää kehittäjän omana kokeilutyökaluna,
   mutta rinnakkaista tuotantotason toteutusta ei rakenneta (CODEX_START §8).

Suositus muuttuu, jos spike-ajo osoittaa esim. että C#-lisäosan lataus tai lapsiprosessin käynnistys
ei toimi Revit 2027:ssä, tai että pyRevit toimii merkittävästi luotettavammin.

## 7. Avoimet kysymykset spike-ajolle

1. Latautuuko allekirjoittamaton per-user-lisäosa, ja millainen turvallisuuskehote näytetään?
2. Mitä `Room.Name` palauttaa verrattuna `ROOM_NAME`-parametriin?
3. Onko `Room.Volume` 0, kun tilavuuslaskenta ei ole päällä mallissa?
4. Miten sijoittamattomat (`Location == null`), sulkeutumattomat (pinta-ala 0) ja päällekkäiset huoneet näkyvät?
5. Palauttavatko `FromRoom`/`ToRoom` odotetut huoneet ikkunoille viimeisessä vaiheessa (phase)?
6. Tunnistetaanko ulkoseinät luotettavasti `WallType`-funktiosta (Exterior)?
7. Kauanko 100–500 huoneen luku kestää?
8. Käynnistyykö CPython-lapsiprosessi Revitistä, ja kauanko käynnistys kestää (virustorjunta)?
9. Säilyvätkö ääkköset (huonenimet) koko ketjun läpi Windowsissa?
10. Toimiiko pyRevit 7.x Revit 2027:ssä tällä koneella, ja millä moottorilla?

## Lähteet

- Autodesk: [Revit 2027 SDK: .NET 10 Migration and Key API Changes](https://blog.autodesk.io/revit-2027-sdk-net-10-api-changes-and-additions/)
- Autodesk: [Migrating Revit to .NET 10](https://help.autodesk.com/cloudhelp/2027/ENU/Revit-WhatsNew/files/GUID-8D7A4715-EAF8-4BD1-BE78-061F900D0BCE.htm)
- [What's New in Revit API 2027 – RVTDocs](https://rvtdocs.com/2027/whats-new/)
- [Autodesk Community: DOTNET 10](https://forums.autodesk.com/t5/revit-api-forum/dotnet-10/td-p/14008220)
- [Autodesk Community: Revit 2027 ManifestSettings deduplication](https://forums.autodesk.com/t5/revit-api-forum/revit-2027-manifestsettings-deduplication-mechanism-from-revit/td-p/14105252)
- [AVAIL for Revit 2027 Updates](https://helpcenter.getavail.com/avail-for-revit-2027-updates)
- pyRevit: [Release v7.0.0](https://github.com/pyrevitlabs/pyRevit/releases/tag/v7.0.0.26278+2233), [Issue #3302](https://github.com/pyrevitlabs/pyRevit/issues/3302), [Issue #3275](https://github.com/pyrevitlabs/pyRevit/issues/3275), [6.4.0](http://pyrevitlabs.io/posts/6.4.0-release/), [6.5.0](http://pyrevitlabs.io/posts/6.5.0-release/), [pyRevitfile](https://github.com/pyrevitlabs/pyRevit/blob/master/pyRevitfile)
- Dynamo: [Dynamo Updates 4.0.2 (What's New in 2027)](https://help.autodesk.com/cloudhelp/2027/ENU/Revit-WhatsNew/files/GUID-7938D2D7-12E2-47EB-B382-2FDC88A3B643.htm), [PythonNet3 migration guide](https://dynamobim.org/dynamo-pythonnet3-upgrade-a-practical-guide-to-migrating-your-dynamo-graphs/)
- IPC: [atomatiq/InterprocessCommunication](https://github.com/atomatiq/InterprocessCommunication), [Avoid Idling](https://blog.autodesk.io/avoid-idling/)
- NuGet: [Nice3point.Revit.Api.RevitAPI](https://www.nuget.org/packages/Nice3point.Revit.Api.RevitAPI)
