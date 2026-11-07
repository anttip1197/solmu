# Vaatimusindeksi

Alkuperäinen vaatimusindeksi (FND-001). Lähteet: `CODEX_START.md` ja `ADDENDUM-0001`.
Vaatimukset tarkennetaan omiin dokumentteihinsa sitä mukaa kuin vastaavat tehtävät alkavat.

**Prioriteetit:** `Must` · `Should` · `Could`
**Toteutuksen tila:** `Not started` · `In progress` · `Implemented` (koodi + testit) · `Verified` (hyväksymiskriteeri todennettu) · `Deferred`
**Testausviite:** testitiedosto tai `–` jos testejä ei vielä ole.

## Tunnisteet

| Etuliite | Alue | Tila |
|---|---|---|
| `FR-REV` | Revit-toiminnot | Vahvistettu (CODEX_START §12) |
| `FR-AI` | AI-toiminnot | Vahvistettu |
| `FR-HTG` | Lämmityssuunnittelu | Vahvistettu |
| `FR-DXF` | DXF-toiminnot | Vahvistettu |
| `FR-DATA` | Datasetit | Vahvistettu |
| `FR-ML` | Koneoppiminen | Vahvistettu |
| `NFR` | Ei-toiminnalliset | Vahvistettu |
| `FR-GEO` | Geometria ja huoneiden muodostus | **Ehdotus** – odottaa käyttäjän hyväksyntää |
| `FR-CALC` | Insinöörilaskennat (ilmavirrat, lämpöhäviöt, tehontarve) | **Ehdotus** – odottaa käyttäjän hyväksyntää |

## Revit (FR-REV)

| ID | Kuvaus | Prio | Hyväksymiskriteeri | Tila | Testi |
|---|---|---|---|---|---|
| FR-REV-001 | Huoneiden tunnisteiden, tasojen ja geometrian lukeminen Revit 2027 -mallista | Must | Valituista huoneista saadaan sopimuksen mukainen serialisoitu kuvaus; testattu Revit 2027:ssä | Not started (spike-probe olemassa, ei ajettu Revitissä) | `docs/testing/revit-2027-spike-protocol.md` |
| FR-REV-002 | Ikkunoiden, ulkoseinien ja olemassa olevien patterien lukeminen | Must | Huoneeseen liittyvät elementit tunnistetaan ja serialisoidaan | Not started | – |
| FR-REV-003 | Revit-yksiköiden muunnos eksplisiittisiin SI-yksiköihin | Must | Muunnokset testattu tunnetuilla arvoilla | Not started | – |
| FR-REV-004 | Vain hyväksyttyjen muutosten vienti malliin hallitussa transaktiossa | Must | Ilman hyväksyntää muutosta ei voi suorittaa; transaktio perutaan virheessä | Not started | – |
| FR-REV-005 | Muutoksen tuloksen tarkastus (`Verified` erillään `Applied`-tilasta) | Must | Toteutus luetaan takaisin ja verrataan hyväksyttyyn ehdotukseen | Not started | – |
| FR-REV-006 | Revit API -olioita ei siirretä prosessien välillä | Must | Rajapinnan tietosopimukset ovat serialisoitavia; sopimustestit | In progress (spike: serialisoitavat DTO:t + stdio, ADR-0003) | `tests/integration/test_revit_spike_service.py`, `tests/integration/test_csharp_ipc_harness.py` |

## Geometria ja huoneet (FR-GEO, ehdotettu etuliite)

| ID | Kuvaus | Prio | Hyväksymiskriteeri | Tila | Testi |
|---|---|---|---|---|---|
| FR-GEO-001 | Revit- ja DXF-lähteiden normalisointi yhteiseen domain-malliin | Must | Molemmista lähteistä syntyy sama domain-rakenne | Not started | – |
| FR-GEO-002 | Huoneella on pysyvä sisäinen tunniste ja jäljitettävä lähdeviite | Must | Tunniste ei riipu huonenumerosta; lähdeviite sisältää lähdetyypin ja elementtitunnisteen | Implemented (perusoliot) | `tests/unit/test_identity.py` |
| FR-GEO-003 | Huonenumeroiden ei oleteta olevan yksilöllisiä eikä nimien pakollisia | Must | Domain hyväksyy puuttuvat ja toistuvat numerot/nimet | Not started | – |
| FR-GEO-004 | Huone-ehdokas ei muutu vahvistetuksi ilman validointisääntöjen läpäisyä | Must | Tilasiirtymä testattu, ohitus ei mahdollinen | Not started | – |
| FR-GEO-005 | Pinta-alan, korkeuden ja tilavuuden laskenta eksplisiittisin yksiköin | Must | Laskenta testattu poikkeusgeometrioilla | Not started | – |

## Laskennat (FR-CALC, ehdotettu etuliite)

| ID | Kuvaus | Prio | Hyväksymiskriteeri | Tila | Testi |
|---|---|---|---|---|---|
| FR-CALC-001 | Huonekohtaiset tulo-, poisto- ja siirtoilmavirrat erikseen | Must | Tulos sisältää perusteen, oletukset, lähteet, menetelmän ja version | Not started | – |
| FR-CALC-002 | Huonekohtainen lämpöhäviö eriteltynä (seinät, ikkunat, ovet, katto, lattia/maa, ilmanvaihto, vuotoilma) | Must | Osatulokset ja välitulokset tallennetaan; puuttuvat syötteet raportoidaan | Not started | – |
| FR-CALC-003 | Puuttuvia syötteitä ei korvata hiljaisesti oletusarvoilla | Must | Puuttuva syöte estää `Verified`-tilan; testattu | Not started | – |
| FR-CALC-004 | Lämmitystehon tarve lasketaan lämpöhäviöstä erillisenä tuloksena | Must | Lämpöhäviö, tarve, valitun patterin teho ja sijoitus ovat erillisiä käsitteitä | Not started | – |
| FR-CALC-005 | Sovellettavat suomalaiset säädökset ja standardit versioineen dokumentoidaan ennen vaatimustenmukaisuuslaskentaa | Must | Dokumentti hyväksytty käyttäjän toimesta | Not started | – |

## Lämmityssuunnittelu (FR-HTG)

| ID | Kuvaus | Prio | Hyväksymiskriteeri | Tila | Testi |
|---|---|---|---|---|---|
| FR-HTG-001 | Huonekohtaiset patterien alustavat sijoitusehdotukset | Must | Ehdotukset validoidaan deterministisesti ennen näyttämistä | Not started | – |
| FR-HTG-002 | Patterin mitoitusta ei väitetä oikeaksi ilman mitoituslämpötiloja, suoritusarvoja ja menetelmää | Must | Puuttuvat tiedot näkyvät varoituksena | Not started | – |
| FR-HTG-003 | Patteriperheiden rekisteri | Should | Rekisteri on versioitu ja validoitu | Not started | – |

## AI (FR-AI)

| ID | Kuvaus | Prio | Hyväksymiskriteeri | Tila | Testi |
|---|---|---|---|---|---|
| FR-AI-001 | AI tuottaa rakenteisen, skeemalla validoitavan ehdotuksen | Must | Virheellinen AI-vastaus hylätään | Not started | – |
| FR-AI-002 | AI ei tuota teknisiä arvoja (lämpöhäviö, teho, ilmavirta) | Must | Sopimus ei salli näitä kenttiä AI-lähteestä | Not started | – |
| FR-AI-003 | Mock AI -adapteri testausta varten | Must | Testit ajettavissa ilman ulkoista palvelua | Not started | – |
| FR-AI-004 | Malliaineistoa ei lähetetä ulkoiseen palveluun ilman hyväksyttyä käytäntöä | Must | Käytäntö dokumentoitu; lähetys estetty oletuksena | Not started | – |

## DXF (FR-DXF), datasetit (FR-DATA), ML (FR-ML)

| ID | Kuvaus | Prio | Hyväksymiskriteeri | Tila | Testi |
|---|---|---|---|---|---|
| FR-DXF-001 | DXF-arkkitehtipiirustusten sisäänluku samaan huonedomainiin | Should | Määritellään DXF-vaiheessa | Deferred | – |
| FR-DATA-001 | Aineiston alkuperä, lisenssi ja käyttöoikeus tallennetaan | Must | Aineistoa ei käytetä ilman dokumentoitua oikeutta | Deferred | – |
| FR-ML-001 | ML-mallien koulutus ja arviointi | Could | Määritellään ML-vaiheessa | Deferred | – |

## Ei-toiminnalliset (NFR)

| ID | Kuvaus | Prio | Hyväksymiskriteeri | Tila | Testi |
|---|---|---|---|---|---|
| NFR-001 | Domain-moduuli on tuotavissa ja testattavissa ilman Revit-asennusta | Must | Testi varmistaa, ettei `heating_ai.domain` tuo Revit-/pyRevit-/`clr`-moduuleja | Verified | `tests/unit/test_domain_isolation.py` |
| NFR-002 | Revitistä riippumattomat testit ajettavissa ilman Revitiä | Must | `python -m pytest` toimii puhtaassa Python-ympäristössä | Verified | `tests/unit/` |
| NFR-003 | Ei salaisuuksia tai asiakasaineistoa versionhallinnassa | Must | `.gitignore` estää yleiset aineistotyypit; tarkastus CI:ssä (FND-004) | In progress | – |
| NFR-004 | Laskentatulokset ovat toistettavia ja jäljitettäviä (syötteet, yksiköt, menetelmä, versio) | Must | Versioidut laskentasopimukset | Not started | – |
| NFR-005 | Tilat erotettu: ehdotus luotu / validoitu / hyväksytty / Applied / Verified sekä addendumin geometria- ja laskentatilat | Must | Tilamalli ja siirtymätestit (FND-008) | Not started | – |
| NFR-006 | Auditointitiedot tallennetaan jokaisesta mallimuutoksesta | Must | Auditointiloki sisältää ehdotuksen, hyväksynnän, toteutuksen ja tarkastuksen | Not started | – |
