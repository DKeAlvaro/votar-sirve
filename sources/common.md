# Common inputs

## INE_IPC290751_290750 — Spanish CPI, deflator for every chart
- Publisher: INE. Table 24077 "Índice general nacional. Series desde enero de 1961" (series IPC290751,
  levels; the API only returns levels from 2002-01) and table 76134 (series IPC290750, 12-month
  variation in %, since 1962-01).
- API: https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/IPC290751?date=20020101:20301231 and
  .../IPC290750?date=19600101:20301231. Downloaded 2026-11-24.
- Method: levels 2002-01 onward; earlier months back-chained L(m-12) = L(m)/(1+yoy(m)/100)
  (one rounding step of the published 1-decimal variation per year). Annual average of 12 months.
  Rebased so 2025 average = 100. Script: scripts/common_cpi.py.
- Check: 2002->2025 +66.6%, identical to INE base-2021 series IPC251852 (2002-2025).
- Output: data/clean/common_cpi_es.csv (cpi_annual_avg 1962-2025, cpi_monthly 1962-01..latest).
