# Chart C - Where do young people want to work? (public / private / own business, 1984 vs 2024)

Verdict: NOT FEASIBLE with identical wording from open primary sources as of 2026-11-25. No `data/clean/cC_*.csv` written, because nothing meets the primary-source and identical-wording rules.

## What was checked
| Source | Result |
|---|---|
| INJUVE Informe Juventud en España 2024 (vol I, II, resumen; `data/raw/cC/`) and Encuesta de Juventud 2023 (EJ190) | Text searched: no preferred-sector question (funcionario / empresa privada / cuenta propia). Crosstab xlsx at `injuve.es/observatorio/demografia-e-informacion-general/cruces-encuesta-de-juventud-2023-ej-190` not searched cell by cell; the report text has no such item |
| INJUVE Informe Juventud en España 2020 (`data/raw/cC/IJE2020.pdf`) | Section 4.2 "ocupación ideal": open question, coded by occupation type, class and gender, not by sector. Not comparable |
| Informe Juventud 1984/85 (Fundación Santa María) | No open digital version found |
| CIS youth surveys | No CIS study with an identical sector-preference question found via search; the catalogue needs manual browsing |
| Not used (non-primary / different wording) | Cámara de Comercio de Sevilla E-2026, Círculo Formación, ABANCA/Praxis, Funcas, Fundación Barrié: private surveys of students, no 1984 |

## Best candidate for a real comparison (needs registration)
ISSP Work Orientations (1989, 1997, 2005, 2015; GESIS cumulation ZA8797). 1997 and 2015: "Suppose you could decide on your work situation at present. Which would you prefer?" with pairs employee / self-employed and private business / government or civil service. 2005: "Suppose you were working and could choose between different kinds of jobs ...". Spain from 1997 (not 1989), NL from 1989. Gives about 1997-2015, never 1984-2024. Alvaro: GESIS login, download ZA8797, cross by age.

Eurobarometer Flash 283 (2009) and 354 (2012) on entrepreneurship ask employee vs self-employed (PDFs in `data/raw/c08/eb/`): no public/private split, no 1984.

CIS: browse the catalogue (cis.es/es/estudios/catalogo) for 1984-1990 youth or employment studies with "funcionario / empresa privada / por cuenta propia", if the 1984 start matters.
