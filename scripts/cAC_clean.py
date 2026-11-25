"""Charts A and C: weighted shares by age group from the GESIS microdata -> data/clean.

Inputs (run first: scripts/cAC_extract.py, scripts/cA_eb_waves.py build):
  data/interim/cA_micro.csv     Mannheim EB trend file ZA3521, `better`, 1980-2001
  data/interim/cA_eb_waves.csv  single EB waves 1996-2025, 'life in general, next 12 months'
  data/interim/cC_micro.csv     ISSP Work Orientations cumulation ZA8797
Outputs: data/clean/cA_expect.csv, data/clean/cC_issp.csv (tidy: date,geo,group,variable,value,unit,source_id)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INT, CLEAN = ROOT / "data/interim", ROOT / "data/clean"

# ZA number -> fieldwork year (EB autumn waves; 7649 is summer 2020, 7780 Feb-Mar 2021, 7902 Jun-Jul 2022)
EB_YEAR = {"ZA2898": 1996, "ZA2959": 1997, "ZA3085": 1998, "ZA3693": 2002, "ZA3938": 2003, "ZA4229": 2004,
           "ZA4414": 2005, "ZA4526": 2006, "ZA4565": 2007, "ZA4819": 2008, "ZA4994": 2009, "ZA5449": 2010,
           "ZA5567": 2011, "ZA5685": 2012, "ZA5876": 2013, "ZA5932": 2014, "ZA6643": 2015, "ZA6788": 2016,
           "ZA6928": 2017, "ZA7489": 2018, "ZA7601": 2019, "ZA7649": 2020, "ZA7780": 2021, "ZA7902": 2022,
           "ZA8779": 2023, "ZA8905": 2024, "ZA9130": 2025}


def age_group(a):
    return np.where((a >= 18) & (a <= 29), "18-29", np.where(a >= 50, "50+", None))


def shares(df, ans, w, keys, src, unit="pct"):
    rows = []
    for k, g in df.groupby(keys):
        rec = dict(zip(keys, k))
        for v in ["better", "same", "worse", "dk"]:
            rows.append({**rec, "variable": v, "value": round(float(np.average(g[ans] == v, weights=g[w])) * 100, 2),
                         "unit": unit, "source_id": src})
        rows.append({**rec, "variable": "n", "value": len(g), "unit": "respondents", "source_id": src})
    return rows


def cA():
    t = pd.read_csv(INT / "cA_micro.csv")
    t = t[t.nation1.isin([3, 12]) & t.better.isin([1, 2, 3, 8])].copy()
    t["geo"] = t.nation1.map({3: "NL", 12: "ES"})
    t["ans"] = t.better.map({1: "better", 2: "same", 3: "worse", 8: "dk"})
    t["group"] = age_group(t.age)
    t = t[t.group.notna()].rename(columns={"year": "date"})
    rows = shares(t, "ans", "wnation", ["date", "geo", "group"], "GESIS ZA3521 (Mannheim EB trend file) var better")

    w = pd.read_csv(INT / "cA_eb_waves.csv")
    w["geo"] = w.iso.str.strip()
    w["date"] = w.za.map(EB_YEAR)
    w["group"] = age_group(w.age)
    w = w[w.group.notna() & w.date.notna()]
    for za, g in w.groupby("za"):
        rows += shares(g, "life", "w", ["date", "geo", "group"], f"GESIS {za} (Eurobarometer) expectations: life in general")
    out = pd.DataFrame(rows)
    out["date"] = out.date.astype(int)
    out = out[["date", "geo", "group", "variable", "value", "unit", "source_id"]].sort_values(["geo", "group", "variable", "date"])
    out.to_csv(CLEAN / "cA_expect.csv", index=False)
    p = out[out.variable == "better"].pivot_table(index="date", columns=["geo", "group"], values="value")
    print(p.round(1).to_string())


def cC():
    d = pd.read_csv(INT / "cC_micro.csv")
    geo = {724: "ES", 528: "NL", 276: "DE", 620: "PT", 250: "FR"}
    d = d[d.country.isin(geo)].copy()
    d["geo"] = d.country.map(geo)
    d["group"] = np.where(d.AGE.between(18, 29), "18-29", np.where(d.AGE >= 30, "30+", None))
    d = d[d.group.notna()]
    rows = []
    items = {"v21": ("prefer_government", "Suppose you could choose: working in a private business (1) or for the government or civil service (2)"),
             "v19": ("prefer_self_employed", "Suppose you could choose: being an employee (1) or being self-employed (2)")}
    for v, (name, _) in items.items():
        for (y, g_, grp), s in d.groupby(["year", "geo", "group"]):
            x = s[s[v].isin([1, 2])]
            if len(x) < 30:
                continue
            allx = s[s[v].isin([1, 2, -8])]
            rows += [
                {"date": y, "geo": g_, "group": grp, "variable": name, "value": round(float(np.average(x[v] == 2, weights=x.WEIGHT)) * 100, 2),
                 "unit": "pct_of_those_choosing", "source_id": "GESIS ZA8797 ISSP Work Orientations " + v},
                {"date": y, "geo": g_, "group": grp, "variable": name + "_cantchoose", "value": round(float(np.average(allx[v] == -8, weights=allx.WEIGHT)) * 100, 2),
                 "unit": "pct", "source_id": "GESIS ZA8797 ISSP Work Orientations " + v},
                {"date": y, "geo": g_, "group": grp, "variable": name + "_n", "value": len(x), "unit": "respondents",
                 "source_id": "GESIS ZA8797 ISSP Work Orientations " + v},
            ]
    out = pd.DataFrame(rows)[["date", "geo", "group", "variable", "value", "unit", "source_id"]]
    out.to_csv(CLEAN / "cC_issp.csv", index=False)
    print(out[out.variable.isin(["prefer_government", "prefer_self_employed"])].pivot_table(
        index=["variable", "group", "geo"], columns="date", values="value").round(1).to_string())


if __name__ == "__main__":
    import sys
    for k in sys.argv[1:] or ["cA", "cC"]:
        {"cA": cA, "cC": cC}[k]()
