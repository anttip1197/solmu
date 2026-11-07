# ADR-0005: Koneoppimisen ja tekoälyn rooli insinööriarvoissa

- **Tila:** Proposed
- **Päivämäärä:** 2026-11-07
- **Päättäjä:** Projektin omistaja
- **Liittyy:** ADDENDUM-0001 §5–6, ADDENDUM-0002 §5, AGENTS.md §5, FR-AI-002, FR-CALC-001, FR-CALC-003

## Konteksti

Omistajan tavoite on, että koneoppimismalli tunnistaa ulkovaipan, huoneet, tilat ja ikkunat ja voi
tuottaa tilojen ilmamäärät (ADDENDUM-0002). ADDENDUM-0001 kieltää ilmavirtojen keksimisen ja
vaatii deterministisen laskentamoottorin. Tarvitaan sääntö, joka sallii ML:n hyödyn mutta pitää
mitoituksen jäljitettävänä.

## Päätösehdotus

Jokaisella laskennan syötearvolla on **lähdetyyppi**:

| Lähdetyyppi | Esimerkki | Saa käyttää laskennassa |
|---|---|---|
| `model` | Revit- tai DXF-geometriasta luettu mitta | Kyllä, kun geometria on validoitu |
| `rule` | Sääntötaulukosta (tilatyyppi × S-luokka) johdettu ilmavirta | Kyllä |
| `project_default` | Omistajan oletus, esim. +21 °C oleskelutila | Kyllä |
| `expert` | Asiantuntijan syöttämä tai muuttama arvo | Kyllä |
| `ml_estimate` / `ai_estimate` | ML-mallin ehdottama ilmavirta tai tilatyyppi | **Ei suoraan.** Vasta kun asiantuntija on hyväksynyt arvon, jolloin lähteeksi tulee `expert` ja alkuperäinen arvio säilyy |

Lisäksi:
1. ML/AI saa tunnistaa geometriaa ja luokitella tiloja. Tunnistus on ehdokas, kunnes se on validoitu
   (ADDENDUM-0001 §4).
2. ML-ehdotus näytetään sääntöarvon rinnalla. Jos ne poikkeavat toisistaan, käyttäjää varoitetaan.
3. Arviosta tallennetaan malli, malliversio, syötteet ja luottamus.
4. Laskentatulos voi olla `Verified` vain, jos kaikkien syötteiden lähde on sallittu.

## Seuraukset

- ML:n hyöty saadaan tunnistukseen ja tarkistukseen, mutta mitoitusvastuu säilyy säännöillä ja asiantuntijalla.
- ADDENDUM-0001 §5:n sääntö pysyy voimassa: ML ei tuota mitoitusarvoa ohi sääntöjen ja hyväksynnän.
- Lähdetyyppi on osa laskentasopimuksia (FND-005, CALC-001).

## Vaihtoehdot

| Vaihtoehto | Arvio |
|---|---|
| ML-arvo käytetään suoraan | Ei ehdoteta: ristiriidassa ADDENDUM-0001:n kanssa, ei jäljitettävissä säädöksiin |
| ML kielletään insinööriarvoissa kokonaan | Ei ehdoteta: menettää tunnistuksen ja ristiintarkistuksen hyödyn |
| **ML ehdottaa, sääntö tai asiantuntija ratkaisee** | **Ehdotettu** |
