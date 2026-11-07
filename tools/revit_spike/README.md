# FND-002 Revit 2027 spike

**Spike-koodia, ei tuotantokoodia.** Tarkoitus on kerätä näyttöä ADR-0002:lle ja ADR-0003:lle.
Kaikki probet ovat vain lukevia. Ajo-ohje: [docs/testing/revit-2027-spike-protocol.md](../../docs/testing/revit-2027-spike-protocol.md).

| Hakemisto | Sisältö | Vaatii Revitin |
|---|---|---|
| `python_service/spike_service.py` | CPython-palvelu, JSON-rivit stdin/stdoutin yli, vain stdlib | Ei |
| `csharp/Solmu.Spike.Ipc` | Probe-DTO:t ja stdio-asiakas (`net10.0`) | Ei |
| `csharp/Solmu.Spike.Harness` | Konsolisovellus: testaa IPC:n Python-palvelua vasten | Ei |
| `csharp/Solmu.Spike.RevitAddin` | Revit 2027 -lisäosa (`net10.0-windows`), `IExternalCommand`, read-only | Ajo kyllä, käännös ei |
| `pyrevit/Solmu.extension` | pyRevit-pushbutton, sama probe IronPythonilla | Kyllä |

## Ilman Revitiä (Linux/Windows/macOS)

```bash
python -m pytest tests/integration
```

```bash
dotnet run --project tools/revit_spike/csharp/Solmu.Spike.Harness -c Release -- python tools/revit_spike/python_service/spike_service.py
```

Revit-lisäosa käännetään NuGet-referenssikirjastoja vasten (`Nice3point.Revit.Api.*` 2027.3.0).
Kirjastoja ei kopioida tulosteeseen, vaan Revit tarjoaa omansa ajon aikana.

## Spike-protokolla (`solmu-spike` v1)

Kuvattu tiedoston `spike_service.py` alussa. **Ei tuotantosopimus.** Tuotantosopimukset määritellään FND-005:ssä.
