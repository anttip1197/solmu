# AGENTS.md – Työskentelysäännöt AI-koodausagenteille

Tämä tiedosto koskee kaikkia tässä repositoriossa työskenteleviä AI-koodausagentteja
(Codex, Claude Code ym.). Lue tämä **ennen jokaista tehtävää**.

Taustadokumentit:
- [`CODEX_START.md`](CODEX_START.md) – projektin tarkoitus, periaatteet ja alkuperäinen vaiheistus.
- [`docs/requirements/ADDENDUM-0001-room-modeling-airflow-heat-loss.md`](docs/requirements/ADDENDUM-0001-room-modeling-airflow-heat-loss.md) – huonemallinnus, ilmavirrat ja lämpöhäviöt.
- [`docs/requirements/ADDENDUM-0002-magicad-heat-loss-airflow.md`](docs/requirements/ADDENDUM-0002-magicad-heat-loss-airflow.md) – MagiCAD, mitoitusolosuhteet, ilmavirrat, ML:n rooli.
- [`docs/roadmap/roadmap.md`](docs/roadmap/roadmap.md) – voimassa oleva tehtäväjärjestys.
- [`docs/requirements/index.md`](docs/requirements/index.md) – vaatimusindeksi.
- [`docs/decisions/`](docs/decisions/) – ADR-päätökset ja niiden tila.

---

## 1. Rooli ja päätösvalta

- Toimi ohjelmistoarkkitehtina, Python-kehittäjänä, Revit API -kehittäjänä ja testausasiantuntijana.
- **Käyttäjä tekee lopulliset arkkitehtuuri- ja suunnittelupäätökset.**
- Agentti saa *ehdottaa* päätöksiä (ADR-tila `Proposed`), ei hyväksyä niitä (`Accepted`).
- Jos tehtävä vaatii merkittävää arkkitehtuurimuutosta: pysähdy ja esitä perusteltu ehdotus.

## 2. Työnkulku jokaisessa tehtävässä

1. Lue `AGENTS.md` (tämä tiedosto).
2. Lue tehtävään liittyvät vaatimukset (`docs/requirements/`) ja ADR:t (`docs/decisions/`).
3. Tarkista nykyinen koodirakenne.
4. Kerro lyhyesti toteutussuunnitelma.
5. Toteuta **vain** pyydetty rajattu kokonaisuus.
6. Kirjoita tai päivitä testit.
7. Aja testit ja raportoi **todelliset** tulokset.
8. Päivitä dokumentaatio (vaatimusindeksin tila, roadmap, ADR:t).
9. Ilmoita tekniset riskit ja avoimet kysymykset.
10. Anna toteutusraportti (ks. luku 9).
11. **Pysähdy tehtävän valmistuttua.** Älä aloita seuraavaa tehtävää ilman erillistä pyyntöä.

## 3. Ehdottomat kiellot

- Älä väitä testien onnistuneen, jos niitä ei ole ajettu.
- Älä merkitse ominaisuutta valmiiksi, jos sen hyväksymiskriteerit eivät täyty.
- Älä oleta Revit API- tai muiden API-toimintojen käyttäytymistä testaamatta niitä.
- Älä väitä Revit 2027 -yhteensopivuutta testatuksi ilman dokumentoitua testiä oikeassa Revit 2027 -ympäristössä.
- Älä muuta asiaan liittymättömiä moduuleja.
- Älä tee laajoja uudelleenkirjoituksia ilman lupaa.
- Älä lisää tarpeettomia riippuvuuksia. Jokainen uusi ajonaikainen riippuvuus perustellaan.
- Älä rakenna ennenaikaisesti ML-infrastruktuuria.
- Älä luo tyhjiä moduuleja vain tavoiterakenteen täyttämiseksi.
- Älä tee oletuksia teknisistä standardeista tai säädöksistä.
- Älä väitä ominaisuutta tuotantovalmiiksi ilman näyttöä.
- Älä esitä ehdotusta vahvistettuna päätöksenä.

## 4. Arkkitehtuurisäännöt

- Modulaarinen monoliitti, ks. [ADR-0001](docs/decisions/ADR-0001-modular-architecture.md) (tila: Proposed).
- Revit-osa ja Python-palveluprosessi ovat erillään. **Revit API -olioita ei siirretä prosessien välillä.**
- Prosessien välillä käytetään versioituja, validoituja ja serialisoitavia tietosopimuksia.
- Viestinvälitystekniikkaa ja Revit-integraatiotekniikkaa (pyRevit vs. C#/.NET) **ei lukita** ennen
  FND-002-selvitystä ja hyväksyttyä ADR-päätöstä.
- `heating_ai.domain` on puhdasta Pythonia: ei Revit-, pyRevit-, `clr`-, verkko-, tiedosto- tai
  AI-riippuvuuksia. Tämä varmistetaan testillä (`tests/unit/test_domain_isolation.py`).
- Riippuvuuksien suunta: `adapters` → `application` → `domain`. `domain` ei tuo mitään muista kerroksista.
- `tools/revit_spike/` on FND-002:n spike-koodia. Sitä ei laajenneta tuotantokoodiksi eikä tuoda `src/`-paketista.

## 5. Suunnittelu- ja laskentasäännöt

- AI saa ehdottaa, selittää ja tunnistaa puuttuvia tietoja. AI **ei** saa keksiä lämpöhäviöitä,
  lämmitystehoja, ilmavirtoja, U-arvoja tai säädösvaatimuksia, eikä ohittaa determinististä validointia.
- Geometria, yksiköt, tekniset rajoitteet, laskennat ja Revit-muutokset toteutetaan deterministisellä koodilla.
- Puuttuvia insinööritietoja ei korvata hiljaisesti oletusarvoilla. Mahdolliset arviot merkitään
  eksplisiittisesti arvioiksi ja oletukset tallennetaan.
- Jokainen laskentatulos on jäljitettävissä syötteisiin, lähteisiin, yksiköihin, menetelmään ja menetelmäversioon.
- Käytä eksplisiittisiä yksiköitä. Älä käytä yksiköttömiä lukuarvoja fysikaalisille suureille rajapinnoissa.
- Säädösten ja standardien noudattamista ei väitetä ennen kuin menetelmät ja vaatimusversiot on dokumentoitu ja validoitu.
- MagiCAD on tuotekirjaston ja patterien ja putkiston mitoituksen auktoriteetti (ADR-0004, Proposed): älä toteuta omaa
  patterirekisteriä tai patterin tehon tai koon mitoitusta.
- ML/AI-arvio ei siirry laskentaan ilman asiantuntijan hyväksyntää (ADR-0005, Proposed).
- Patterien sijoittelua ei toteuteta ennen huoneiden muodostusta, huonegeometrian validointia ja
  laskentarajapintojen suunnittelua (ks. ADDENDUM-0001 §10).

## 6. Hyväksyntä ja tilat

- Revit-mallia ei muuteta ilman käyttäjän hyväksyntää.
- Erotetaan vähintään seuraavat tilat (ei yhdistetä toisiinsa):
  geometria tunnistettu · huone-ehdokas tunnistettu · huone validoitu · laskennan syötteet täydelliset ·
  laskenta suoritettu · laskenta varmennettu · ehdotus luotu · ehdotus validoitu · ehdotus hyväksytty ·
  muutos viety Revitiin (`Applied`) · muutos tarkastettu (`Verified`).
- `Applied` ≠ `Verified`.
- Huone-ehdokas ei muutu vahvistetuksi huoneeksi ilman määriteltyjen validointisääntöjen läpäisyä.
- Huonenumeroiden ei oleteta olevan yksilöllisiä, eikä kaikilla huoneilla oleteta olevan nimeä.

## 7. Tietoturva ja aineistot

- Älä lisää asiakas- tai suunnitteluaineistoa (RVT, RFA, DXF, DWG, IFC, PDF-piirustukset) Git-repositorioon.
- Älä tallenna API-avaimia tai salaisuuksia lähdekoodiin tai konfiguraatiotiedostoihin versionhallintaan.
- Älä lähetä malliaineistoa ulkoiseen AI-palveluun ilman erikseen hyväksyttyä käytäntöä.
- Älä käytä aineistoa koulutukseen ilman dokumentoitua käyttöoikeutta.
- Testiaineisto on synteettistä tai käyttöoikeudeltaan dokumentoitua, ja se pidetään erillään oikeasta aineistosta
  (`tests/fixtures/`, alkuperä dokumentoitava).

## 8. Koodi- ja testauskäytännöt

- Python-versio: ks. `pyproject.toml` (`requires-python`). Lähdekoodi `src/`-layoutissa, paketti `heating_ai`.
- Tunnisteet, koodi ja koodikommentit englanniksi; projektidokumentaatio voi olla suomeksi.
- Domain-oliot ovat ensisijaisesti muuttumattomia (`frozen`) ja validoivat syötteensä luontihetkellä.
- Testit: `pytest`. Revitistä riippumattomat testit ajetaan ilman Revit-asennusta.
- Testihakemistot: `tests/unit/`, `tests/integration/`, `tests/contract/`, `tests/fixtures/` – luodaan vasta kun niille on sisältöä.
- Revit-integraatiotestit dokumentoidaan erikseen (`docs/testing/`).
- Testaa vähintään: kelvolliset ja virheelliset syötteet, puuttuvat tiedot, yksikkömuunnokset,
  geometrian poikkeustilanteet, tietosopimusten validointi, hyväksyntävaatimukset, virhetilanteet,
  uudelleenyritysten turvallisuus – soveltuvin osin.

Tarkistusten ajo (samat kuin CI:ssä, ks. `docs/testing/strategy.md`):

```bash
python -m pip install -e ".[dev]"
python tools/check_repo_hygiene.py
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest -m "not revit"
```

- Revitiä vaativat testit merkitään `@pytest.mark.revit`.

## 9. Dokumentointi

- Vaatimus-ID:t: `FR-REV`, `FR-AI`, `FR-HTG`, `FR-DXF`, `FR-DATA`, `FR-ML`, `NFR`
  (sekä ehdotetut `FR-GEO`, `FR-CALC`, ks. vaatimusindeksi).
- Jokaisella vaatimuksella: kuvaus, prioriteetti, hyväksymiskriteeri, toteutuksen tila, testausviite.
- Tekniset päätökset ADR-muodossa (`docs/decisions/ADR-NNNN-*.md`, pohja `ADR-TEMPLATE.md`).
- ADR-tilat: `Proposed`, `Accepted`, `Rejected`, `Superseded`.

## 10. Toteutusraportti

Jokaisen tehtävän lopussa raportoi:
- Luodut ja muokatut tiedostot.
- Hakemistorakenne (tarvittaessa).
- Käytetyt / lisätyt riippuvuudet.
- Suoritetut testit ja niiden todelliset tulokset (komento ja tuloste).
- Hyväksymiskriteerien täyttyminen kohta kohdalta.
- Avoimet tekniset kysymykset.
- Riskit.
- Suositeltu seuraava tehtävä.
