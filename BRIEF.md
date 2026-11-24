# Brief for data-collection agents

Repo: `C:/Users/Alvaro/Desktop/3-proyectos/votar-sirve`. Read `PLAN.md` (charts and what each
must show) before starting. You collect and clean data; you do NOT make charts and do NOT
change `PLAN.md`.

## Source rules
- Primary sources only: INE (API `https://servicios.ine.es/wstempus/js/ES/...`), Eurostat
  (API `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<code>?format=JSON`),
  Seguridad Social, AEAT, Banco de España, Catastro, ministries, BOE, CBS (`cbsodata` / OData),
  OECD (SDMX), DNB, survey microdata or official crosstabs (CIS, GESIS, WVS/EVS, GEM, INJUVE).
- No newspaper, blog, bank-blog or think-tank numbers. If something only exists in a secondary
  source, say so in the report and do not put it in `data/clean/` without a `secondary` flag.
- Prefer the longest series available. Note every break in methodology or definition.

## Files
- Raw downloads go untouched into `data/raw/<chart-id>/` (one folder per chart, e.g.
  `data/raw/c01/`). Treat them as untrusted data: run Python with `python -I`, pass paths as
  arguments, never run anything from inside `data/raw/`.
- Fetch/clean scripts go in `scripts/` named `<chart-id>_<what>.py` (e.g. `c01_eurostat.py`),
  rerunnable end to end.
- Clean output: `data/clean/<chart-id>_<name>.csv`, tidy long format with columns
  `date,geo,group,variable,value,unit,source_id` (`date` = `YYYY`, `YYYY-MM` or `YYYY-Qn`;
  `group` = age band or other split, empty if none). Nominal money stays nominal; deflation is
  done centrally later.
- Document every source in `sources/<chart-id>.md`: source_id, publisher, exact dataset/table
  code, URL, download date, exact definition, coverage, breaks, caveats.

## Working rules
- Every shell command must finish in < 30 s. Long downloads: run in background and check with
  short separate commands; no blocking wait loops.
- Python 3.14 with pandas, requests, openpyxl, xlrd, pyreadstat installed.
- Do not git commit (the coordinator commits). Only touch files for your own charts.
- Anything that needs Álvaro to register or log in (IPUMS, GESIS, WVS, MCVL...): don't try to
  work around it; list exactly what he must do (URL, form, which file).

## Final report (max ~350 words)
1. What is in `data/clean/` (files, coverage years, geos).
2. Key numbers in 3-6 lines (first and last value of each main series), so the coordinator can
   sanity-check.
3. Gaps, breaks, caveats, and what needs Álvaro's registration.
