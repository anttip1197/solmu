# Testausstrategia

> Tila: alkuversio (FND-001). CI ja testausrunko tarkentuvat tehtävässä FND-004.

## Testityypit

| Tyyppi | Hakemisto | Vaatii Revitin | Tila |
|---|---|---|---|
| Yksikkötestit | `tests/unit/` | Ei | Käytössä |
| Sopimustestit (tietosopimusten validointi ja serialisointi) | `tests/contract/` | Ei | FND-005 |
| Integraatiotestit (Python-puoli) | `tests/integration/` | Ei | Myöhemmin |
| Revit-integraatiotestit | dokumentoidaan erikseen | **Kyllä** | FND-002/FND-007 |

Hakemistot luodaan vasta kun niihin tulee testejä.

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
