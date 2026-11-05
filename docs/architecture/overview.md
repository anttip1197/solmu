# Arkkitehtuurin yleiskuvaus

> Tila: luonnos (FND-001). Perustuu [ADR-0001](../decisions/ADR-0001-modular-architecture.md) (Proposed).
> Revit-integraatiotekniikka ja prosessien välinen viestintä ovat **avoimia** (FND-002).

## 1. Kokonaiskuva

Järjestelmä on **modulaarinen monoliitti**, joka koostuu kahdesta prosessista:

```mermaid
flowchart LR
    subgraph Revit["Revit 2027 -prosessi (tekniikka avoin, FND-002)"]
        R1["Dokumentin ja elementtien luku"]
        R2["Yksikkömuunnokset"]
        R3["Hyväksyttyjen muutosten transaktiot"]
        R4["Toteutuksen tarkastus"]
    end
    subgraph Py["Python-palveluprosessi (heating_ai)"]
        P1["application"]
        P2["domain"]
        P3["laskenta & validointi"]
        P4["AI-orkestrointi"]
        P5["auditointi"]
    end
    Revit <-- "versioidut, serialisoitavat tietosopimukset\n(IPC-tekniikka avoin)" --> Py
    P4 -. "hallittu, hyväksytty käytäntö" .-> AI["Ulkoinen AI-palvelu"]
```

- Revit API -olioita ei siirretä prosessirajan yli.
- Rajapinta koostuu versioiduista, validoiduista tietosopimuksista (FND-005).
- Ulkoinen AI on erillinen, hallittu osa (hybridimalli). Malliaineistoa ei lähetetä ilman hyväksyttyä käytäntöä.

## 2. Kerrokset Python-prosessissa

| Kerros | Vastuu | Saa riippua |
|---|---|---|
| `domain` | Domain-käsitteet, invariantit, tilat. Puhdas Python. | Vain standardikirjasto |
| `application` | Käyttötapaukset ja työnkulut (tuleva) | `domain`, `contracts` |
| `contracts` | Versioidut prosessirajan ja laskennan tietosopimukset (tuleva, FND-005) | `domain` |
| `adapters/*` | Revit-, LLM- ja tallennusliitokset (tuleva) | `application`, `contracts`, `domain` |

Muut tavoiterakenteen moduulit (`geometry`, `heating_planner`, `validation`, `audit`, `dxf_ingestion`, …)
luodaan vasta niitä vastaavien tehtävien alkaessa.

## 3. Käsittelyputki (ADDENDUM-0001 §2)

```mermaid
flowchart TD
    S1["1. Lähdegeometrian tuonti"] --> S2["2. Rakennusosien ja rajojen tunnistus"]
    S2 --> S3["3. Huoneiden tunnistus ja muodostus"]
    S3 --> S4["4. Huonegeometrian ja topologian validointi"]
    S4 --> S5["5. Pinta-ala, korkeus, tilavuus"]
    S5 --> S6["6. Rakennusfysiikan ja LVI-syötteiden keruu"]
    S6 --> S7["7. Ilmavirtalaskenta"]
    S7 --> S8["8. Lämpöhäviölaskenta"]
    S8 --> S9["9. Lämmitystehon tarve"]
    S9 --> S10["10. Patterien sijoitusehdotukset"]
    S10 --> S11["11. Ehdotusten validointi"]
    S11 --> S12["12. Käyttäjän hyväksyntä"]
    S12 --> S13["13. Muutokset Revitiin (Applied)"]
    S13 --> S14["14. Tarkastus (Verified) ja auditointi"]
```

Vaiheet 1–9 ja 11 ovat deterministisiä. AI osallistuu vain vaiheeseen 10 (ja avustaa
käyttötarkoituksen tunnistuksessa sekä puuttuvien tietojen tunnistamisessa).

## 4. Erotettavat tilat

Geometria tunnistettu → huone-ehdokas → huone validoitu → syötteet täydelliset → laskenta suoritettu →
laskenta varmennettu → ehdotus luotu → ehdotus validoitu → ehdotus hyväksytty → Applied → Verified.

Tilamallin toteutus on tehtävän FND-008 (ja GEO-/CALC-tehtävien) vastuulla.

## 5. Nykyinen toteutus (FND-001)

- `heating_ai.domain.identity`: `RoomId` (pysyvä sisäinen tunniste), `SourceType`, `SourceReference`
  (jäljitettävä viite lähdegeometriaan). Nämä toteuttavat ADDENDUM-0001 §1 periaatteen
  "stable internal identity and traceable relationship to its source geometry" perustason.
- Ei Revit-, AI-, DXF- tai ML-toteutusta.
