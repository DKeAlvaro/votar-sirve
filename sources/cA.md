# Chart A - Do young people expect things to get better? (ES vs NL, young vs 50+, 1985-2025)

Verdict: NOT FEASIBLE from open data as of 2026-11-25 (age-by-country results need microdata behind a registration or a form). Only question wordings are in `data/clean/cA_wording.csv`.

## Comparability table
| Question | Exact wording | Years | Access |
|---|---|---|---|
| EB trend `BETTER` | "So far as you are concerned, do you think that 19xx will be better or worse than 19xx-1?" (better / same / worse; "same" spontaneous from EB36) | EB14 (1980) to EB42 (1994) in the Mannheim trend file; Spain in EB from 1985 | Codebook (ICPSR 3384, `data/raw/cA/cb3384.pdf`, p.312-313) has totals per EB wave only, all countries pooled. Microdata: GESIS ZA3521 / ICPSR 3384, free after registration |
| EB expectations (life in general, economy of country, personal job, household finances) | "What are your expectations for the year to come (the next twelve months): will (...) be better, worse or the same, when it comes to ...?" | EB44 (1995) to 2019; EB34-42 (1990-94) used a 5-point a lot better..a lot worse scale | GESIS EB trend page `gesis.org/en/eurobarometer-data-service/overview/eb-trends-trend-files/list-of-trends/expectations` (403 for scripted fetch; wording from a search snippet, verify in a browser). Microdata per wave (ZA numbers) after GESIS login. Standard EB reports publish totals by country, age tables only in some annexes |
| EB expectations, new wording | "In one year's time, do you think that each of the following will be better, worse, or the same as today?" | EB94.2 (2020) onward | wording break; same access |
| CIS barometer | "Y, ¿cree Ud. que dentro de un año su situación económica personal será mejor, igual o peor que ahora?" (item A.5 in ECIS3277, March 2020) | Monthly barometers (series page for the current assessment starts 1992-04-24) | Marginals PDF open (e.g. `cis.es/documents/d/cis/es3203marpdf`: Jan 2018 better 20.3 / same 61.2 / worse 9.0, total only). Age crosstabs only in each study's tables or via microdata/FID form (`cis.es/es/catalogo-estudios/fid`). Mode breaks: PAPI/CAPI to CATI 2020-04, weighting change 2023-11 |

There is no NL equivalent outside the Eurobarometer.

## What Alvaro must do (not attempted)
1. GESIS account (free): download ZA3521 (EB Trend File) and per-wave ZA files; variable `better`, and for 1995+ the "expectations" items (QA/QB in Standard EB). Cross by age and country (Spain, Netherlands).
2. CIS: request microdata through the form (FID or each study page), item "dentro de un año ... situación económica personal". A harmonised 2021+ file exists at `gastiaso.github.io/barometros` (third party, CC BY 4.0, not primary).

Best long series if done: EB `BETTER` 1985-1994 + EB expectations 1995-2025 (wording breaks 1995 and 2020).
