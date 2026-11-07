# Arkkitehtuuripäätökset (ADR)

Tilat: `Proposed` · `Accepted` · `Rejected` · `Superseded`.
Vain projektin omistaja voi muuttaa tilan `Accepted`-tilaan. Pohja: [ADR-TEMPLATE.md](ADR-TEMPLATE.md).

| ADR | Otsikko | Tila | Päivämäärä |
|---|---|---|---|
| [ADR-0001](ADR-0001-modular-architecture.md) | Modulaarinen monoliitti ja erillinen Python-palveluprosessi | Proposed | 2026-11-05 |
| [ADR-0002](ADR-0002-revit-integration-technology.md) | Revit 2027 -integraatiotekniikka: C#/.NET 10 -lisäosa | Proposed (odottaa Revit-ajoa) | 2026-11-07 |
| [ADR-0003](ADR-0003-process-boundary-ipc.md) | Prosessien välinen viestintä: lapsiprosessi + JSON-rivit stdion yli | Proposed (odottaa Revit-ajoa) | 2026-11-07 |
| [ADR-0004](ADR-0004-magicad-role.md) | MagiCAD tuotekirjaston ja mitoituksen auktoriteettina, järjestelmä laskee lämpöhäviön | Proposed | 2026-11-07 |
| [ADR-0005](ADR-0005-ml-in-engineering-values.md) | ML/AI ehdottaa, sääntö tai asiantuntija ratkaisee insinööriarvot | Proposed | 2026-11-07 |

## Odottavat päätökset

| Aihe | Tehtävä | Tila |
|---|---|---|
| Revit 2027 -integraatiotekniikka (pyRevit vs. C#/.NET 10) | FND-002 | ADR-0002 Proposed; lukitaan vasta Revit 2027 -ajon jälkeen |
| Prosessien välinen viestintätekniikka | FND-002 / FND-003 | ADR-0003 Proposed |
| Python-ajoympäristön jakelu käyttäjän koneelle | FND-003 | Ei aloitettu |
| Lisäosan allekirjoitusvarmenne ja all-users-asennus | ennen tuotantoasennusta | Ei aloitettu |
| Tietosopimusten skeema- ja validointitekniikka | FND-005 | Ei aloitettu |
| Lämpöhäviön laskentamenetelmä, ulkoilman mitoituslämpötilat, ilmamäärätaulukot (Talotekniikka-Info, S1–S3) | ennen CALC-004/006 | Odottaa omistajan lähdeaineistoa (ADDENDUM-0002 §8) |
| Patterin vientitapa malliin MagiCAD-tuotteena | MAG-001 | Ei aloitettu |
| Sovellettavat suomalaiset säädökset, standardit ja laskentamenetelmät versioineen | ennen CALC-004/006 | Ei aloitettu |
| Ulkoisen AI-palvelun käyttö- ja aineistokäytäntö | ennen FR-AI-toteutusta | Ei aloitettu |
