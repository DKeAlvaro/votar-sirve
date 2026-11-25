"""c09: minimum monthly autonomo (RETA) contribution, years with a verified BOE figure.
Values transcribed from the BOE texts listed in sources/c09.md (raw copies in data/raw/c09/hist and data/raw/c09).
Output: data/clean/c09_min_fee_history.csv. Nominal money (peseta years converted at 166.386 pts/EUR).
GAPS: 1980-87, 1989-96, 2000-2022 not collected (see sources/c09.md)."""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PTS = 166.386
# year: (min base per month, currency, rate % (contingencias comunes+profesionales+cese+FP+MEI as applicable), source_id, flag)
D = {
    1988: (51390, "ESP", 28.8, "BOE-A-1987-28781", ""),
    1997: (106440, "ESP", 28.3, "BOE-A-1997-1701", ""),
    1998: (110580, "ESP", 28.3, "BOE-A-1998-1806", ""),
    1999: (113340, "ESP", 28.3, "BOE-A-1999-1132", ""),
    2023: (751.63, "EUR", 31.2, "RDL13-2022_DT1+LGSS_DT43", "rate_assumed_from_2026_structure(28.3+1.3+0.9+0.1+MEI0.6)"),
    2024: (735.29, "EUR", 31.3, "RDL13-2022_DT1+LGSS_DT43", "rate_assumed_from_2026_structure(MEI0.7)"),
    2025: (653.59, "EUR", 31.4, "Orden_PJC/178/2025_not_downloaded", "base_from_search_snippet_not_raw;rate_assumed(MEI0.8)"),
    2026: (653.59, "EUR", 31.5, "BOE-A-2026-7296_art18", ""),
}
rows = []
for y, (b, cur, r, sid, flag) in sorted(D.items()):
    eur = b / PTS if cur == "ESP" else b
    note = "min_fee_year>=2023_uses_tabla_reducida_tramo1" if y >= 2023 else "single_minimum_base"
    rows += [[y, "ES", "", "min_base_month_eur", round(eur, 2), "EUR/month", sid],
             [y, "ES", "", "contribution_rate_pct", r, "pct", sid + ("|" + flag if flag else "")],
             [y, "ES", "", "min_fee_month_eur", round(eur * r / 100, 2), "EUR/month", sid + ("|" + flag if flag else "") + "|" + note]]
    if cur == "ESP":
        rows.append([y, "ES", "", "min_base_month_pesetas", b, "ESP/month", sid])
out = os.path.join(ROOT, "data", "clean", "c09_min_fee_history.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "geo", "group", "variable", "value", "unit", "source_id"])
    w.writerows(rows)
for r in rows:
    if r[3] == "min_fee_month_eur":
        print(r[0], r[4])
