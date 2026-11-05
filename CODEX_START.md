# Projektin käynnistysohje – AI-avusteinen Revit-lämmityssuunnittelu

> **Huom.:** Tämän dokumentin vaiheistusta (luku 11) on täydennetty ja osittain korvattu
> dokumentilla [`docs/requirements/ADDENDUM-0001-room-modeling-airflow-heat-loss.md`](docs/requirements/ADDENDUM-0001-room-modeling-airflow-heat-loss.md).
> Voimassa oleva tehtäväjärjestys on [`docs/roadmap/roadmap.md`](docs/roadmap/roadmap.md).
> Alkuperäinen sisältö on säilytetty alla muuttamattomana.

## 1. Projektin tarkoitus

Tämän projektin tavoitteena on rakentaa tuotantokäyttöön soveltuva AI-avusteinen suunnittelujärjestelmä, joka toimii Autodesk Revit 2027 -ympäristössä.

Järjestelmän ensimmäinen käyttötapaus on vesikiertoisen patterilämmityksen alustava suunnittelu huonekohtaisesti.

Käyttäjä pystyy:
- Lukemaan Revit-mallista huoneiden tiedot ja geometrian.
- Tunnistamaan huoneiden seinät, ikkunat ja muut sijoitteluun vaikuttavat rakenteet.
- Pyytämään tekoälyltä patterien alustavia sijoitusehdotuksia.
- Tarkastelemaan ehdotuksia ennen niiden viemistä Revit-malliin.
- Hyväksymään tai hylkäämään ehdotukset.
- Luomaan hyväksytyt elementit Revit-malliin hallitusti.

Projektin myöhemmässä vaiheessa järjestelmään rakennetaan myös DXF-pohjaisten arkkitehtipiirustusten käsittely, datasetien muodostaminen sekä koneoppimismallien koulutus ja arviointi.

Tavoite ei ole pelkkä demonstraatio tai prototyyppi. Arkkitehtuurin, tietomallien, testauksen ja dokumentaation tulee tukea myöhempää tuotantokäyttöä.

---

## 2. Projektin vahvistetut lähtötiedot

Seuraavat asiat ovat projektin lähtökohtia:

| Ominaisuus | Päätös |
|---|---|
| BIM-ohjelmisto | Autodesk Revit 2027 |
| Lämmitysjärjestelmä | Vesikiertoinen patterilämmitys |
| Ensimmäinen käyttötapaus | Huoneiden ja patterien alustava sijoittelu |
| Säädösympäristö | Suomi |
| AI-arkkitehtuuri | Hybridimalli |
| Paikallinen GPU | Ei käytettävissä |
| Datasetien lähteet | DXF ja Revit |
| Kehitystiimi | Yksi kehittäjä ja AI-koodausagentit |
| Autonomian taso | Valvottu automaatio |
| Tuotantotavoite | Kyllä |

Tärkeää: Suomen säädösympäristön tukeminen ei tarkoita automaattisesti viranomaisvaatimusten täyttymistä. Vaatimukset, laskentamenetelmät ja niiden versiot on dokumentoitava ja validoitava erikseen.

---

## 3. Codexin rooli

Toimi projektissa kokeneena ohjelmistoarkkitehtina, Python-kehittäjänä, Revit API -kehittäjänä ja testausasiantuntijana.

Älä kuitenkaan tee itsenäisiä laajoja arkkitehtuurimuutoksia ilman perustelua.

Työskentele seuraavilla periaatteilla:

1. Suunnittele ennen toteutusta.
2. Toteuta pienissä, rajatuissa kokonaisuuksissa.
3. Noudata olemassa olevaa arkkitehtuuria.
4. Kirjoita testit toteutuksen yhteydessä.
5. Dokumentoi tekniset päätökset.
6. Älä oleta API-toiminnallisuuksia testaamatta niitä.
7. Älä väitä testien onnistuneen, jos niitä ei ole ajettu.
8. Älä merkitse ominaisuutta valmiiksi, jos sen hyväksymiskriteerit eivät täyty.
9. Älä muuta asiaan liittymättömiä moduuleja.
10. Ilmoita epäselvyydet ennen merkittävää toteutusta.

Käyttäjä tekee lopulliset arkkitehtuuri- ja suunnittelupäätökset.

---

## 4. Tekninen pääarkkitehtuuri

Tavoitteena on modulaarinen monoliitti, jonka Revit-integraatio ja erillinen Python-palveluprosessi ovat selkeästi erotettu toisistaan.

### Revit-osa

Revitissä toimiva komponentti vastaa:
- Revit-dokumentin lukemisesta.
- Huoneiden ja elementtien tietojen hakemisesta.
- Geometrian lukemisesta.
- Revit-yksiköiden käsittelystä.
- Hyväksyttyjen muutosten toteuttamisesta.
- Revit-transaktioista.
- Muutosten tuloksen tarkastamisesta.

### Python-osa

Erillinen Python-prosessi vastaa:
- Sovelluslogiikasta.
- AI-yhteyksistä.
- Suunnitelmien muodostamisesta.
- DXF-tiedostojen käsittelystä.
- Datasetien muodostamisesta.
- Validointilogiikasta.
- Myöhemmästä ML-koulutuksesta.
- Auditoinnista ja tulosten tallentamisesta.

### Rajapinta

Revit- ja Python-osan välillä käytetään versioituja, validoituja tietosopimuksia.

Revit API -olioita ei saa siirtää prosessien välillä.

Käytä serialisoitavia tietomalleja ja dokumentoitua viestinvälitystä.

Älä lukitse viestinvälitystekniikkaa ennen kuin sille on dokumentoitu perusteltu ADR-päätös.

---

## 5. Tavoiteltu moduulirakenne

Rakenna projektia asteittain seuraavan rakenteen pohjalta:

```text
project/
│
├── AGENTS.md
├── CODEX_START.md
├── README.md
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── architecture/
│   ├── requirements/
│   ├── decisions/
│   ├── testing/
│   └── roadmap/
│
├── src/
│   └── heating_ai/
│       ├── domain/
│       ├── application/
│       ├── contracts/
│       ├── geometry/
│       ├── dxf_ingestion/
│       ├── dataset_builder/
│       ├── ml_training/
│       ├── llm_orchestrator/
│       ├── heating_planner/
│       ├── validation/
│       ├── audit/
│       └── adapters/
│           ├── revit/
│           ├── llm/
│           └── storage/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── fixtures/
│
└── tools/
```

Tämä on tavoiterakenne, ei vaatimus luoda heti tyhjiä hakemistoja.

Luo vain moduulit, joille on konkreettista sisältöä ja käyttötarkoitusta.

---

## 6. Suunnitteluperiaatteet

### 6.1 AI ei saa tehdä teknisiä oletuksia

AI voi:
- Ehdottaa patterin sijaintia.
- Ehdottaa patterin suuntaa.
- Selittää ehdotuksen perusteet.
- Tunnistaa puuttuvia lähtötietoja.
- Tuottaa rakenteisen suunnitelmaehdotuksen.

AI ei saa:
- Keksiä huoneen lämpöhäviötä.
- Keksiä patterin lämmitystehoa.
- Väittää mitoitusta oikeaksi ilman laskentaperusteita.
- Ohittaa determinististä validointia.
- Muuttaa Revit-mallia ilman hyväksyntää.

### 6.2 Deterministinen logiikka

Geometria, yksiköt, tekniset rajoitteet ja Revit-mallin muutokset toteutetaan tavallisella ohjelmakoodilla.

AI:n tuottama suunnitelma validoidaan ennen hyväksyttäväksi näyttämistä.

### 6.3 Käyttäjän hyväksyntä

Työnkulun on oltava:

1. Lue lähtötiedot.
2. Muodosta suunnitelmaehdotus.
3. Validoi ehdotus.
4. Näytä käyttäjälle ehdotus ja mahdolliset varoitukset.
5. Pyydä hyväksyntä.
6. Toteuta hyväksytyt muutokset Revitissä.
7. Tarkista toteutuksen tulos.
8. Tallenna auditointitiedot.

Revit-mallin muuttaminen ilman käyttäjän hyväksyntää on kielletty.

### 6.4 Tilojen erottaminen

Erota vähintään seuraavat käsitteet:
- Ehdotus luotu.
- Ehdotus validoitu.
- Käyttäjä hyväksynyt.
- Muutos viety Revit-malliin.
- Muutos tarkastettu onnistuneeksi.

`Applied` ja `Verified` eivät tarkoita samaa asiaa.

---

## 7. Ensimmäisen käyttötapauksen rajaus

Ensimmäinen toimiva kokonaisuus on huonekohtainen patterien alustava sijoittelu.

Työnkulku:

1. Käyttäjä valitsee Revitistä huoneen tai huoneita.
2. Järjestelmä lukee huoneiden tunnisteet, tasot ja geometrian.
3. Järjestelmä tunnistaa saatavilla olevat ikkunat, ulkoseinät ja olemassa olevat patterit.
4. Järjestelmä tarkistaa puuttuvat lähtötiedot.
5. AI muodostaa sijoitusehdotuksen.
6. Deterministinen logiikka tarkistaa ehdotuksen.
7. Käyttäjä tarkastelee ehdotusta.
8. Käyttäjä hyväksyy tai hylkää ehdotuksen.
9. Hyväksytyt patterit luodaan Revit-malliin.
10. Toteutus tarkistetaan ja kirjataan lokiin.

Ensimmäisen version ulkopuolelle jätetään:
- Automaattinen putkireititys.
- Hydraulinen mitoitus.
- Automaattinen lämpöhäviölaskenta.
- Automaattisesti koulutettu ML-malli.
- Valmiin suunnitelman automaattinen hyväksyminen.

---

## 8. Revit 2027 -tekninen päätös

Revit 2027 -integraation teknologiaa ei saa lukita ennen erillistä yhteensopivuustestiä.

Toteuta ensin selvitys:
- pyRevit-yhteensopivuudesta.
- Python-ajoympäristöstä.
- Revit API -toiminnallisuuksista.
- Oman C#/.NET 10 -lisäosan toteutettavuudesta.
- Prosessien välisestä viestinnästä.

Tee näiden perusteella ADR-päätös.

Valitse yksi tuotantokäytön Revit-integraatioratkaisu.

Älä rakenna rinnakkaisia tuotantotason pyRevit- ja C#-toteutuksia ilman erillistä hyväksyttyä syytä.

---

## 9. Tietoturva ja aineiston käsittely

DXF- ja Revit-aineistoilla voi olla erilaisia käyttöoikeuksia ja luottamuksellisuustasoja.

Siksi:
- Älä lähetä malliaineistoa ulkoiseen AI-palveluun ilman erikseen määriteltyä hyväksyttyä käytäntöä.
- Älä tallenna API-avaimia lähdekoodiin.
- Älä lisää asiakas- tai suunnitteluaineistoa Git-repositorioon.
- Älä käytä aineistoa mallien koulutukseen ilman dokumentoitua käyttöoikeutta.
- Erota testiaineisto oikeasta suunnitteluaineistosta.
- Dokumentoi aineiston alkuperä, lisenssi ja käyttöoikeudet.

Hybridimalli tarkoittaa, että paikallinen aineistonkäsittely ja ulkoinen AI-palvelu ovat erillisiä ja hallittuja osia.

---

## 10. Testausvaatimukset

Jokaisen toteutetun toiminnon tulee sisältää asianmukaiset testit.

Testaa vähintään:
- Kelvolliset syötteet.
- Virheelliset syötteet.
- Puuttuvat tiedot.
- Yksikkömuunnokset.
- Geometrian poikkeustilanteet.
- Tietosopimusten validointi.
- Hyväksyntävaatimukset.
- Virhetilanteiden käsittely.
- Uudelleenyritysten turvallisuus.

Revitistä riippumattomat testit tulee voida ajaa ilman Revit-asennusta.

Revit-integraatiotestit dokumentoidaan erikseen.

---

## 11. Kehityksen vaiheistus

Noudata seuraavaa etenemisjärjestystä.

### Vaihe 1 – Foundation

- FND-001 Repository ja projektin säännöt.
- FND-002 Revit 2027 -yhteensopivuusselvitys.
- FND-003 Python-ympäristö ja riippuvuuksien erottelu.
- FND-004 CI ja testausrunko.
- FND-005 Tietomallit ja rajapintasopimukset.
- FND-006 Konfiguraatio, lokitus ja virhekoodit.
- FND-007 Revitin read-only-adapteri.
- FND-008 Hyväksyntä- ja tehtävätilamalli.
- FND-009 Mock AI -adapteri.
- FND-010 Foundationin hyväksymistestit.

### Vaihe 2 – Huoneiden lukeminen ja geometria

- ROOM-001 Huonegeometrian normalisointi.
- ROOM-002 Seinien ja ikkunoiden tunnistus.
- ROOM-003 Patteriperheiden rekisteri.
- ROOM-004 Deterministiset sijoittelusäännöt.
- ROOM-005 AI:n sijoitusehdotus.
- ROOM-006 Visuaalinen esikatselu.
- ROOM-007 Hyväksytty Revit-muutos.
- ROOM-008 Käyttäjän hyväksymistestit.

### Vaihe 3 – DXF ja datasetit

- DXF-tiedostojen sisäänluku.
- Geometrian tunnistus.
- Merkintöjen ja huoneiden tunnistus.
- Datasetin rakenne.
- Annotointiprosessi.
- Aineiston alkuperä- ja käyttöoikeustiedot.

### Vaihe 4 – ML ja tuotantovalmius

- Mallien koulutusympäristö.
- Mallien arviointi.
- Vertailu deterministiseen ja LLM-pohjaiseen ratkaisuun.
- Malliversiointi.
- Suorituskykytestit.
- Tietoturva- ja käyttöoikeustarkastukset.

Älä siirry seuraavaan vaiheeseen ennen edellisen hyväksymiskriteerien täyttymistä.

---

## 12. Vaatimusten ja päätösten dokumentointi

Käytä yksilöllisiä vaatimus-ID-tunnuksia:

- `FR-REV-xxx`: Revit-toiminnot.
- `FR-AI-xxx`: AI-toiminnot.
- `FR-HTG-xxx`: lämmityssuunnittelun toiminnot.
- `FR-DXF-xxx`: DXF-toiminnot.
- `FR-DATA-xxx`: datasetit.
- `FR-ML-xxx`: koneoppiminen.
- `NFR-xxx`: ei-toiminnalliset vaatimukset.

Jokaisella vaatimuksella tulee olla:
- Kuvaus.
- Prioriteetti.
- Hyväksymiskriteeri.
- Toteutuksen tila.
- Testausviite.

Tekniset päätökset dokumentoidaan ADR-muodossa.

Päätöksen tila merkitään:
- Proposed
- Accepted
- Rejected
- Superseded

Älä esitä ehdotusta vahvistettuna päätöksenä.

---

## 13. Codexin työskentelymalli

Kun saat uuden tehtävän:

1. Lue ensin `AGENTS.md`.
2. Lue tehtävään liittyvät vaatimukset.
3. Tarkista nykyinen koodirakenne.
4. Kerro lyhyesti, miten aiot toteuttaa tehtävän.
5. Toteuta vain pyydetty rajattu kokonaisuus.
6. Kirjoita tai päivitä testit.
7. Aja testit.
8. Päivitä dokumentaatio.
9. Ilmoita mahdolliset tekniset riskit.
10. Anna toteutusraportti.

Älä:
- Tee laajoja uudelleenkirjoituksia ilman lupaa.
- Lisää tarpeettomia riippuvuuksia.
- Rakenna ennenaikaisesti ML-infrastruktuuria.
- Tee oletuksia teknisistä standardeista.
- Väitä ominaisuutta tuotantovalmiiksi ilman näyttöä.

Jos tehtävän toteutus edellyttää merkittävää arkkitehtuurimuutosta, pysähdy ja esitä perusteltu ehdotus.

---

# 14. Ensimmäinen tehtävä Codexille

## TASK FND-001 – Initialize the project foundation

Aloita projektin Foundation-vaiheesta.

Toteuta seuraavat asiat:

1. Luo projektin perusrakenne.
2. Luo `README.md`.
3. Luo `AGENTS.md`.
4. Luo tämä `CODEX_START.md` projektin juureen.
5. Luo alkuperäinen vaatimusindeksi.
6. Luo arkkitehtuurin yleiskuvaus.
7. Luo `ADR-0001` modulaarisesta arkkitehtuurista.
8. Luo `pyproject.toml`.
9. Luo `.gitignore`.
10. Luo minimaalinen domain-esimerkki.
11. Varmista, että domain voidaan tuoda ja testata ilman Revit-asennusta.
12. Luo vähintään yksi automatisoitu testi.

### Rajaukset

Älä tässä tehtävässä:
- Toteuta patterien sijoittelua.
- Toteuta DXF-käsittelyä.
- Lisää ML-kirjastoja.
- Toteuta varsinaista AI-yhteyttä.
- Tee Revit API -abstraktioita ennen FND-002-selvitystä.
- Väitä Revit 2027 -yhteensopivuutta testatuksi.
- Luo tyhjiä moduuleja vain tavoiterakenteen täyttämiseksi.

### Hyväksymiskriteerit

Tehtävä on valmis, kun:

- Projektilla on selkeä käynnistysohje.
- Dokumentaatio on versionhallinnassa.
- AGENTS.md sisältää Codexin työskentelysäännöt.
- Domain-moduuli voidaan tuoda ilman Revit-riippuvuuksia.
- Testit suoritetaan onnistuneesti.
- Teknisten päätösten tila on dokumentoitu.
- Projektin seuraava tehtävä on selkeästi FND-002.

### Lopputulosraportti

Raportoi:
- Luodut ja muokatut tiedostot.
- Projektin lopullinen hakemistorakenne.
- Käytetyt riippuvuudet.
- Suoritetut testit ja niiden todelliset tulokset.
- Avoimet tekniset kysymykset.
- Mahdolliset riskit.
- Suositeltu seuraava tehtävä.

**TÄRKEÄÄ: Pysähdy FND-001-tehtävän valmistuttua. Älä aloita FND-002-tehtävää ilman erillistä pyyntöä.**
