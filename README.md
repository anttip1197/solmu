# Solmu – AI-avusteinen Revit-lämmityssuunnittelu

Tuotantokäyttöön tähtäävä, valvotun automaation suunnittelujärjestelmä Autodesk Revit 2027 -ympäristöön.
Ensimmäinen käyttötapaus on vesikiertoisen patterilämmityksen huonekohtainen alustava suunnittelu.

> **Tila:** Foundation-vaihe, FND-001 toteutettu. Revit-integraatiota ei ole vielä toteutettu eikä
> Revit 2027 -yhteensopivuutta ole testattu. Järjestelmä ei tee lämpöhäviö-, ilmavirta- tai
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
│   ├── roadmap/               # Tehtäväjärjestys
│   └── testing/               # Testausstrategia
├── src/heating_ai/
│   └── domain/                # Puhdas domain-malli (ei Revit-riippuvuuksia)
└── tests/
    └── unit/
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

## Seuraava tehtävä

**FND-002 – Revit 2027 -yhteensopivuusselvitys** (ks. [roadmap](docs/roadmap/roadmap.md)).
