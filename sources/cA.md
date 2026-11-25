# Chart A - Do young people expect things to get better? (ES vs NL, 18-29 vs 50+, 1985-2025)

Verdict: built from GESIS microdata (free account) on 2026-11-25. Clean output: `data/clean/cA_expect.csv`
(shares of better / same / worse / don't know, plus n, by year, country and age group, weighted).

## Data
| Years | Source | Wording | Variable |
|---|---|---|---|
| 1980-1994 (ES from 1985) | Mannheim Eurobarometer Trend File 1970-2002, GESIS ZA3521 v2.0.1, doi:10.4232/1.10074 | "So far as you are concerned, do you think that 19xx will be better or worse than 19xx-1?" ("same" not read out) | `better`, weight `wnation` |
| 1995, 1999-2001 | same file (EB44.1, 52.0, 54.1, 56.2) | "What are your expectations for the next twelve months: will (...) be better, worse or the same, when it comes to your life in general?" | `better` |
| 1996-1998, 2002-2025 | 27 standard EB waves, GESIS ZA2898 ... ZA9130 (list with years in `scripts/cAC_clean.py`, GESIS download ids in `sources/cA_eb_waves.txt`) | same as 1995 | "EXPECTATIONS: LIFE IN GENERAL" item (`v37`, `qa5a_1`, `qa2_1`... found by label in `scripts/cA_eb_waves.py`); weight "W1 WEIGHT RESULT FROM TARGET"; age "D11 AGE EXACT" |

The "b" copy of the item in 2008-2020 waves is the Turkish Cypriot community version (empty for ES/NL) and is ignored.
2020 uses EB93.1 (summer, standard QA2 item) because EB94.2 (autumn) switched to the new "in one year's time... living conditions" wording.

## Breaks and caveats
- 1995 wording change ("next year better than this year" -> "life in general, next twelve months", and "same" read out). The site breaks the line at 1994.5; compare within segments and across countries in the same year.
- n per wave: ES 18-29 134-301; NL 18-29 26-302, very small in 2014-2020 (26-67) because of the Dutch online/telephone samples. The site plots 3-year centred means inside each segment; the raw value per year is in the tooltip and in the CSV.
- DK/NA is kept in the denominator.

## Rebuild
1. Download (GESIS login): ZA3521 .dta to `data/raw/cA/`, the waves in `sources/cA_eb_waves.txt` (plus ZA3085) to `data/raw/cA/eb/`.
2. `python -I scripts/cAC_extract.py cA` -> `data/interim/cA_micro.csv`
3. `python -I scripts/cA_eb_waves.py build` -> `data/interim/cA_eb_waves.csv` (`scan` lists the variables it picks)
4. `python -I scripts/cAC_clean.py cA` -> `data/clean/cA_expect.csv`; `python -I scripts/build_site.py cA` -> `docs/data/cA.json`

Not used: CIS barometer item "dentro de un año su situación económica personal" (only totals open; age needs microdata via the FID form; no NL equivalent).
