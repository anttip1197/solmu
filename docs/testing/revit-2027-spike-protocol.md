# FND-002 – Revit 2027 -spike-testiprotokolla

Tämän protokollan ajaa projektin omistaja omalla Revit 2027 -koneellaan. Tulokset kirjataan tämän
dokumentin lopun taulukkoon, ja niiden perusteella ADR-0002 ja ADR-0003 joko hyväksytään tai päivitetään.

Kaikki spike-komennot ovat **vain lukevia**: ne eivät avaa transaktioita eivätkä muuta mallia.

## 0. Valmistelu

**Testimalli:** käytä Revitin esimerkkimallia tai omaa testimallia, jossa on huoneita, ikkunoita ja
ulkoseiniä. Hyvä testimalli sisältää myös hankalia tapauksia: sijoittamaton huone, sulkeutumaton huone,
kaksi huonetta samalla numerolla, nimetön huone, ääkkösiä huonenimissä.

> Raportti-JSONit tallentuvat paikallisesti kansioon `%LOCALAPPDATA%\Solmu\spike\`. **Älä lisää
> asiakasmallien raportteja Gitiin** (AGENTS.md §7). Kirjaa tänne vain tulostaulukko.

**Ohjelmat:**
- Revit 2027 (kirjaa versio ja build: *Tiedosto → Tietoja Revitistä*)
- .NET 10 SDK, vain C#-osioon:

```bash
winget install Microsoft.DotNet.SDK.10
```

- Python 3.12 tai uudempi Python-palvelua varten (python.org tai `winget install Python.Python.3.12`)

**Repositorio:**

```bash
git clone -b claude/focused-tesla-cqgrzr https://github.com/anttip1197/solmu.git C:\dev\solmu
```

Komennot on kirjoitettu Windowsin **komentokehotteelle (cmd)**. PowerShellissä `%MUUTTUJA%` kirjoitetaan muodossa `$env:MUUTTUJA`.

**Python-palvelun ympäristömuuttujat** (molemmat probet käyttävät näitä; muuta polku omaan Python-asennukseesi):

```bash
setx SOLMU_PYTHON "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
```

```bash
setx SOLMU_SPIKE_SERVICE "C:\dev\solmu\tools\revit_spike\python_service\spike_service.py"
```

Käynnistä Revit uudelleen `setx`-komentojen jälkeen, jotta se näkee muuttujat.

## C. C#/.NET 10 -lisäosa (ADR-0002, suositeltu vaihtoehto)

**C1 – Käännös**

```bash
cd C:\dev\solmu\tools\revit_spike\csharp
```

```bash
dotnet build Solmu.Spike.RevitAddin -c Release
```

Odotus: `Build succeeded`, 0 varoitusta.

**C2 – Harness ilman Revitiä (Windowsin IPC)**

```bash
dotnet run --project Solmu.Spike.Harness -c Release -- %SOLMU_PYTHON% %SOLMU_SPIKE_SERVICE%
```

Odotus: `ALL CHECKS PASSED`. Kirjaa ping-aika ja 100 pingin kokonaisaika.

**C3 – Asennus per-user**
1. Kopioi `Solmu.Spike.RevitAddin\bin\Release\net10.0-windows\Solmu.Spike.addin` kansioon
   `%APPDATA%\Autodesk\Revit\Addins\2027\`.
2. Muokkaa kopioidun tiedoston `<Assembly>`-rivi osoittamaan DLL:n absoluuttiseen polkuun, esim.
   `C:\dev\solmu\tools\revit_spike\csharp\Solmu.Spike.RevitAddin\bin\Release\net10.0-windows\Solmu.Spike.RevitAddin.dll`.
3. Käynnistä Revit 2027. Kirjaa, näkyikö turvallisuuskehote ja mitä valitsit (*Load once* riittää).

**C4 – Ajo**
1. Avaa testimalli.
2. *Lisäosat (Add-Ins) → Ulkoiset työkalut (External Tools) → Solmu probe (read-only)*.
3. Aja kerran ilman valintaa (kaikki huoneet) ja kerran, kun 1–3 huonetta on valittuna.
4. Kirjaa dialogin tiedot: Revit-versio, .NET-versio, huonemäärä, lukuaika ja **Python IPC** -rivi.

**C5 – Malli ei muuttunut:** sulje malli. Revitin ei pitäisi kysyä tallennusta probe-ajon takia.

**C6 – Raportin tarkastus:** avaa uusin `probe-csharp-*.json` ja tarkista kohdat 1–6 alla olevasta listasta.

## P. pyRevit (ADR-0002, vertailukohta)

**P1 – Asennus:** asenna pyRevit 7.x per-user (pyrevitlabs GitHub releases). Kirjaa versio ja se,
näkyykö pyRevit-välilehti Revit 2027:ssä. Jos välilehti puuttuu, kirjaa se tulokseksi. Se on tärkeä havainto.

**P2 – Laajennuksen lisäys:**

```bash
pyrevit extensions paths add C:\dev\solmu\tools\revit_spike\pyrevit
```

Lataa sitten pyRevit uudelleen (*pyRevit → Reload*). Jos komento ei toimi, lisää sama kansio
käyttöliittymästä: *pyRevit → Settings → Custom Extension Directories* → *Reload*.

**P3 – Ajo:** välilehti *Solmu → Spike → Solmu probe (read-only)*. Aja sama malli ja samat valinnat kuin C4:ssä.

**P4 – Kirjaa** tulosteikkunasta Python-moottori (`Python engine`), lukuaika ja `Python IPC` -rivi.

**P5 – Raportti:** vertaa `probe-pyrevit-*.json` C#-raporttiin. Huonemäärän, pinta-alojen ja
tunnisteiden pitäisi olla samat.

## M. MagiCAD for Revit (ADR-0004)

Aja C4 mallilla, jossa on **MagiCAD-tiloja (Spaces) ja MagiCADilla sijoitettuja pattereita**, kun MagiCAD on ladattuna.

**M1 – Yhteiselo:** latautuvatko MagiCAD ja Solmu-probe samaan aikaan ilman virheilmoituksia?
Toimiiko MagiCAD normaalisti proben ajon jälkeen?

**M2 – Tunnistus:** dialogin rivi *MagiCAD assemblies loaded* on suurempi kuin 0. Kirjaa raportin
`magi_cad_assemblies`-listan nimet ja versiot.

**M3 – Tilat:** dialogin *MEP spaces* -määrä vastaa mallia. Raportin `spaces`-listasta:
- Mikä parametri sisältää MagiCADin käyttämän **lämmitystehon tarpeen**? Kirjaa parametrin nimi ja `shared_guid`.
- Onko tiloissa MagiCADin ilmavirtaparametreja (tulo/poisto)? Kirjaa nimet.
- Onko `room_id` täytetty, eli onko tila liitetty arkkitehdin huoneeseen?

**M4 – Patterit:** raportin `mechanical_equipment_samples`-listasta MagiCAD-patterin osalta:
- Mitkä parametrit sisältävät tuotekoodin, valmistajan, tehon ja mitoituslämpötilat?
- Onko `space_id` täytetty?

> Kirjaa tänne vain **parametrien nimet ja GUIDit**, ei asiakasmallin arvoja.

## Raportista tarkistettavat asiat (C6/P5)

1. `room.name` vs. `room.element_name`: mitä kumpikin sisältää?
2. `volume_internal`: onko se 0? Onko mallissa tilavuuslaskenta päällä (*Area and Volume Computations*)?
3. Sijoittamaton huone: `is_placed = false`? Sulkeutumaton huone: `area_internal = 0`?
4. Saman numeron huoneet: tuleeko molemmat eri `element_id`:llä ja `unique_id`:llä?
5. Ikkunat: onko `from_room_id`/`to_room_id` täytetty ja `host_wall_function = "Exterior"` ulkoseinille?
6. `area_square_meters` vastaa Revitin näyttämää pinta-alaa (m²)?

## Tulokset

| Kohta | Tulos (OK / FAIL / ei ajettu) | Havainnot |
|---|---|---|
| Revit-versio ja build | | |
| C1 käännös | | |
| C2 harness Windowsissa | | ping ms / 100 pingiä ms |
| C3 asennus, turvallisuuskehote | | |
| C4 ajo, kaikki huoneet | | huoneita / lukuaika ms / IPC |
| C4 ajo, valinta | | |
| C5 malli ei muuttunut | | |
| C6 raportti (kohdat 1–6) | | |
| P1 pyRevit-asennus ja välilehti | | pyRevit-versio |
| P2 laajennus | | |
| P3–P4 ajo | | moottori / lukuaika / IPC |
| P5 vertailu C#-raporttiin | | |
| M1 MagiCAD + probe yhtä aikaa | | |
| M2 MagiCAD-kirjastot tunnistettu | | nimet / versiot |
| M3 tilan lämmitystehon tarpeen parametri | | nimi / GUID |
| M3 tilan ilmavirtaparametrit | | nimet |
| M4 MagiCAD-patterin tuoteparametrit | | nimet |

Ajaja: ____________  Päivämäärä: ____________
