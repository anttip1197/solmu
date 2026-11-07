# Testausstrategia

> Tila: päivitetty FND-004:ssä (CI).

## Testityypit

| Tyyppi | Hakemisto | Vaatii Revitin | Tila |
|---|---|---|---|
| Yksikkötestit | `tests/unit/` | Ei | Käytössä |
| Sopimustestit (tietosopimusten validointi ja serialisointi) | `tests/contract/` | Ei | FND-005 |
| Integraatiotestit (Python-puoli, aliprosessit, C#-harness) | `tests/integration/` | Ei | Käytössä (FND-002) |
| Revit-integraatiotestit | [revit-2027-spike-protocol.md](revit-2027-spike-protocol.md) | **Kyllä** | FND-002: protokolla valmis, ajo odottaa; FND-007 |

Hakemistot luodaan vasta kun niihin tulee testejä.

C#-harness-testi (`tests/integration/test_csharp_ipc_harness.py`) ohitetaan automaattisesti, jos .NET SDK puuttuu.

## Periaatteet

- Revitistä riippumattomat testit ajetaan ilman Revit-asennusta: `python -m pytest`.
- `tests/unit/test_domain_isolation.py` varmistaa, ettei `heating_ai.domain` tuo Revit-,
  pyRevit- tai .NET-siltamoduuleja eikä muita kuin standardikirjaston moduuleja.
- Testiaineisto on synteettistä. Oikeaa suunnitteluaineistoa ei lisätä repositorioon.
- Testituloksia ei raportoida ajamatta testejä; raportissa näytetään komento ja todellinen tuloste.
- Revit 2027 -yhteensopivuutta ei väitetä testatuksi ilman dokumentoitua ajoa oikeassa Revit 2027 -ympäristössä
  (Revit-versio, build, ajoympäristö, päivämäärä, tulos).

## Vähimmäiskattavuus toiminnoittain (soveltuvin osin)

Kelvolliset syötteet · virheelliset syötteet · puuttuvat tiedot · yksikkömuunnokset ·
geometrian poikkeustilanteet · tietosopimusten validointi · hyväksyntävaatimukset ·
virhetilanteet · uudelleenyritysten turvallisuus.

## Jatkuva integraatio (FND-004)

Työnkulku: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml). Ajetaan jokaisesta pushista ja pull requestista.

| Job | Ympäristö | Tarkistukset |
|---|---|---|
| Lint, types, hygiene | Ubuntu, Python 3.12 | `tools/check_repo_hygiene.py`, `ruff check`, `ruff format --check`, `mypy` (strict) |
| Tests | Ubuntu ja Windows × Python 3.12 ja 3.13, .NET 10 | C#-spiken käännös (myös Revit 2027 -lisäosa referenssikirjastoja vasten), `pytest -m "not revit"` |

- Windows-ajo testaa C#–CPython-stdio-viestinnän Windowsissa (ilman Revitiä).
- Revitiä vaativat testit merkitään `@pytest.mark.revit`. CI ei aja niitä, eikä Revit-yhteensopivuutta väitetä CI:n perusteella.
- Hygieniatarkistus estää malli- ja piirustustiedostot (RVT, RFA, DWG, DXF, IFC, PDF ym.), yli 5 Mt:n tiedostot
  ja tunnistettavat salaisuudet. Synteettiset testiaineistot sallitaan hakemistossa `tests/fixtures/synthetic/`.
- Kehitystyökalut (`ruff`, `mypy`, `pytest`) ovat vain `dev`-riippuvuuksia, eivät ajonaikaisia.

Samat tarkistukset paikallisesti:

```bash
python -m pip install -e ".[dev]"
python tools/check_repo_hygiene.py
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest -m "not revit"
```
