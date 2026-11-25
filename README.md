# ¿Sirve de algo votar?

Data study: does voting PP or PSOE change what matters to a young person in Spain (becoming
independent, starting a business)? Spain vs the Netherlands, primary sources only.

**Site:** https://dkealvaro.github.io/votar-sirve/

## How it was done

1. `PLAN.md` — charts, predictions and refutation criteria, committed before any data was
   downloaded (see the first commit).
2. `data/clean/` — tidy CSVs (`date,geo,group,variable,value,unit,source_id`), one prefix per chart.
   Raw downloads are not committed; every `scripts/cNN_*.py` re-fetches them into `data/raw/`.
3. `sources/` — one note per chart: publisher, dataset code, URL, definitions, breaks, caveats.
4. `scripts/build_site.py`, `build_c02_c03.py`, `build_c06.py` — compute the results and write
   `docs/data/*.json`. The page (`docs/`) renders them with Observable Plot.

Money is in 2025 euros, deflated with the INE CPI (`scripts/common_cpi.py`).

## Rebuild

```
python -I scripts/common_cpi.py data/raw/common data/clean
python -I scripts/build_site.py
python -I scripts/build_c02_c03.py
python -I scripts/build_c06.py
# charts A and C need GESIS microdata (free login), see sources/cA.md and sources/cC.md
python -I scripts/cAC_extract.py && python -I scripts/cA_eb_waves.py build && python -I scripts/cAC_clean.py
python -I scripts/build_site.py cA cC
python -m http.server 8765 -d docs
```
