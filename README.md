# Solmu – AI-avusteinen Revit-lämmityssuunnittelu

Tuotantokäyttöön tähtäävä, valvotun automaation suunnittelujärjestelmä Autodesk Revit 2027 -ympäristöön.
Ensimmäinen käyttötapaus on vesikiertoisen patterilämmityksen huonekohtainen alustava suunnittelu.

> **Tila:** Foundation-vaihe. FND-001 valmis. FND-002:n selvitys ja spike ovat valmiit, ja Revit 2027 -ajo
> odottaa ([protokolla](docs/testing/revit-2027-spike-protocol.md)). Revit 2027 -yhteensopivuutta ei ole vielä testattu Revitissä. Järjestelmä ei tee lämpöhäviö-, ilmavirta- tai
> mitoituslaskentaa eikä väitä säädösten täyttymistä.

## Periaatteet lyhyesti

- **Huoneet ensin:** geometria → huoneiden muodostus ja validointi → laskennat → patterisuunnittelu.
- **Deterministinen ydin:** geometria, yksiköt, laskennat ja validointi ovat tavallista, testattavaa koodia.
- **AI ehdottaa, ei päätä:** AI ei keksi teknisiä arvoja eikä ohita validointia.
- **Käyttäjä hyväksyy:** Revit-mallia ei muuteta ilman hyväksyntää; `Applied` ≠ `Verified`.
- **Aineistot pysyvät poissa repositoriosta.**

## Pika-aloitus

Vaatimukset: Python 3.12 tai uudempi. Revit-asennusta **ei** tarvita.

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

```bash
python -m pip install -e ".[dev]"
```

```bash
python -m pytest
```

## Hakemistorakenne

```text
.
├── AGENTS.md                  # AI-agenttien työskentelysäännöt (lue ensin)
├── CODEX_START.md             # Projektin käynnistysohje
├── README.md
├── pyproject.toml
├── docs/
│   ├── architecture/          # Arkkitehtuurin yleiskuvaus
│   ├── decisions/             # ADR-päätökset
│   ├── requirements/          # Vaatimusindeksi ja addendumit
│   ├── research/              # Selvitykset (FND-002)
│   ├── roadmap/               # Tehtäväjärjestys
│   └── testing/               # Testausstrategia ja Revit-testiprotokollat
├── src/heating_ai/
│   └── domain/                # Puhdas domain-malli (ei Revit-riippuvuuksia)
├── tests/
│   ├── unit/
│   └── integration/           # Aliprosessi- ja IPC-testit (ei Revitiä)
└── tools/
    └── revit_spike/           # FND-002 spike: C#-lisäosa, pyRevit-probe, Python-palvelu
```

Muut tavoiterakenteen moduulit (ks. `CODEX_START.md` §5) luodaan vasta kun niille on sisältöä.

## Dokumentaatio

| Dokumentti | Sisältö |
|---|---|
| [AGENTS.md](AGENTS.md) | Työskentelysäännöt |
| [CODEX_START.md](CODEX_START.md) | Tarkoitus, periaatteet, alkuperäinen vaiheistus |
| [ADDENDUM-0001](docs/requirements/ADDENDUM-0001-room-modeling-airflow-heat-loss.md) | Huonemallinnus, ilmavirrat, lämpöhäviöt |
| [Roadmap](docs/roadmap/roadmap.md) | Voimassa oleva tehtäväjärjestys |
| [Vaatimusindeksi](docs/requirements/index.md) | Vaatimukset ja niiden tila |
| [Arkkitehtuuri](docs/architecture/overview.md) | Yleiskuvaus |
| [ADR-hakemisto](docs/decisions/README.md) | Tekniset päätökset |
| [Testausstrategia](docs/testing/strategy.md) | Testauksen periaatteet |
| [FND-002-selvitys](docs/research/FND-002-revit-2027-compatibility.md) | Revit 2027, pyRevit, .NET 10, IPC |
| [Revit 2027 -testiprotokolla](docs/testing/revit-2027-spike-protocol.md) | Ajettava Revitissä |

## Seuraava tehtävä

1. **FND-002:n Revit 2027 -ajo**: projektin omistaja ajaa [testiprotokollan](docs/testing/revit-2027-spike-protocol.md).
2. Päätös ADR-0002:sta ja ADR-0003:sta.
3. Sen jälkeen **FND-003** (Python-ympäristö ja prosessiraja). FND-004 (CI) ei riipu FND-002:sta.
