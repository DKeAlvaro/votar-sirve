# Chart C - Where do young people want to work? (public / private, employee / self-employed)

Verdict: built from GESIS microdata on 2026-11-25, but only for 1997-2005 in Spain (the plan asked 1984 vs 2024).
Clean output: `data/clean/cC_issp.csv`.

## Data
ISSP Work Orientations I-IV Cumulation, GESIS ZA8797 v1.0.0, doi:10.4232/1.14391. Weighted (`WEIGHT`), age 18-29 vs 30+.

Wording, identical in ISSP 1989 (ZA1840 Q8), 1997 (ZA3090 Q8) and 2005 (ZA4350 Q4): "Suppose you were working and could
choose between different kinds of jobs. Which of the following would you personally choose? I would choose..."
- `v21`: working in a private business (1) / working for the government or civil service (2)
- `v19`: being an employee (1) / being self-employed (2)

Not asked in ISSP 2015 (ZA6770). Countries: ES 1997, 2005; NL and DE 1989, 1997, 2005; PT and FR 1997, 2005.
Shares are of those who chose one option; "can't choose" is stored separately (`*_cantchoose`; ES 18-29: 3-8%, NL 18-29: 7-30%).
NL 2005 has only 94 respondents aged 18-29.

## What else was checked (no identical question 1984-2024)
| Source | Result |
|---|---|
| INJUVE Informe Juventud 2020, 2024; Encuesta de Juventud 2023 | no preferred-sector question; 2020 "ocupación ideal" is an open occupation question |
| Informe Juventud 1984/85 | no digital version found |
| CIS | no identical sector-preference item found by search; catalogue not browsed by hand |
| Flash Eurobarometer 283 (2009), 354 (2012) | employee vs self-employed only, no public/private, no 1984 |

## Rebuild
1. Download ZA8797 .dta (GESIS login) to `data/raw/cC/`.
2. `python -I scripts/cAC_extract.py cC`, `python -I scripts/cAC_clean.py cC`, `python -I scripts/build_site.py cC`.
