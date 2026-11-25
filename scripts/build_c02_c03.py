"""c02 (years of salary per flat, rent effort), c03 (young-renter prices vs young salary) and the
extra c05 panel metrics. Writes docs/data/c02.json, docs/data/c03.json, data/clean/c05_panel_extra.csv.
Run: python -I scripts/build_c02_c03.py
"""
import json, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "data", "clean")
OUT = os.path.join(ROOT, "docs", "data")
rd = lambda n: pd.read_csv(os.path.join(CLEAN, f"{n}.csv"), low_memory=False)
dump = lambda n, o: json.dump(o, open(os.path.join(OUT, f"{n}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# ---------- young salary (gross annual mean, 25-34)
s = rd("c02_salaries")
m = s[s.variable == "earn_mean_annual_gross"]
sal = {}
for y in (1995, 2002, 2006):
    g = m[m.date == y].set_index("group").value
    sal[y] = (g["25-29"] + g["30-34"]) / 2
e = m[m.source_id == "INE_EAES_28201"]
for r in e[e.group == "25-34"].itertuples():
    sal[int(r.date)] = r.value
allages = {int(r.date): r.value for r in e[e.group == "all"].itertuples()}
for y in (1995, 2002, 2006):
    allages[y] = m[(m.date == y) & (m.group == "all")].value.iloc[0]

# ---------- c02: years of young salary for an 80 m2 flat
hp = rd("c02_house_price_national_annual")
price = {int(r.date): r.value for r in hp[hp.source_id == "mivau_valor_tasado_libre"].itertuples()}
years_flat = [{"x": y, "y": round(price[y] * 80 / sal[y], 2), "s": "Joven de 25-34"} for y in sorted(sal) if y in price]
years_flat_all = [{"x": y, "y": round(price[y] * 80 / allages[y], 2), "s": "Todas las edades"} for y in sorted(allages) if y in price]
bde = rd("c02_house_price_bde_affordability")
bde["year"] = bde.date.str[:4].astype(int)
bde_a = bde.groupby("year").value.mean()
bde_rows = [{"x": int(y), "y": round(v, 2), "s": "Precio / renta bruta de un hogar (Banco de España)"} for y, v in bde_a.items() if y <= 2026]

# rent effort: Catalonia new-contract rent vs national young salary (monthly gross = annual/12)
r = rd("c02_rents")
inc = r[(r.variable == "incasol_new_contract_rent_mean") & (r.geo == "Catalunya") & (r.date.astype(str).str.len() == 4)]
inc = {int(x.date): x.value for x in inc.itertuples()}
serp = r[r.variable.str.startswith("serpavi_rent_m2_median_apartment_national")]
serp = {int(x.date): x.value for x in serp.itertuples()}
rent_eff = [{"x": y, "y": round(inc[y] / (sal[y] / 12) * 100, 1), "s": "Alquiler nuevo medio en Cataluña"} for y in sorted(inc) if y in sal]
rent_eff += [{"x": y, "y": round(serp[y] * 70 / (sal[y] / 12) * 100, 1), "s": "Alquiler mediano de 70 m² en España (contratos en vigor)"} for y in sorted(serp) if y in sal]
dump("c02", {"years": years_flat + years_flat_all, "bde": bde_rows, "rent": rent_eff})
yf = {d["x"]: d["y"] for d in years_flat}
print("c02 years of young salary per 80m2:", {k: yf[k] for k in sorted(yf) if k in (1995, 2002, 2006, 2008, 2013, 2019, 2024)})
print("c02 BdE price/household income:", {k: round(bde_a[k], 2) for k in (1987, 1995, 2007, 2013, 2025, 2026) if k in bde_a})
print("c02 rent effort:", [(d["x"], d["y"], d["s"][:12]) for d in rent_eff if d["x"] in (2008, 2013, 2019, 2024)])

# ---------- c03: young-renter price index vs young salary, 2008 = 100
w = rd("c03_weights")
w = w[w.group == "young_renter"].pivot_table(index="variable", columns="date", values="value")
g = rd("c03_cpi_groups")
g = g[g.source_id == "INE_24080"].pivot_table(index="date", columns="group", values="value")
cpi_rent = r[r.variable == "cpi_rent_annual_avg"].set_index("date").value
cpi_rent.index = cpi_rent.index.astype(int)
groups = [f"{i:02d}" for i in range(1, 13)]


def weights(year):
    """Young-renter spending shares (12 groups; 04 split into rent and rest). Linear between 2008/2013/2019, 2019 after."""
    pts = [2008, 2013, 2019]
    y = min(max(year, 2008), 2019)
    a = max(p for p in pts if p <= y); b = min(p for p in pts if p >= y)
    t = 0 if a == b else (y - a) / (b - a)
    sh = {k: (1 - t) * w.loc[f"share_ecoicop_{k}", a] + t * w.loc[f"share_ecoicop_{k}", b] for k in groups}
    rent = (1 - t) * w.loc["share_rent", a] + t * w.loc["share_rent", b]
    sh["rent"] = rent
    sh["04"] = sh["04"] - rent
    tot = sum(sh.values())
    return {k: v / tot for k, v in sh.items()}


def basket(rent_series):
    idx = {2008: 100.0}
    for y in range(2009, 2026):
        if y not in rent_series or (y - 1) not in rent_series:
            break
        wt = weights(y - 1)
        rel = {k: g.loc[y, f"ecoicop1_{k}"] / g.loc[y - 1, f"ecoicop1_{k}"] for k in groups}
        rel["rent"] = rent_series[y] / rent_series[y - 1]
        idx[y] = idx[y - 1] * sum(wt[k] * rel[k] for k in wt)
    return idx


b_new = basket(inc)
b_cpi = basket(cpi_rent.to_dict())
cpi_gen = rd("common_cpi_es")
cpi_gen = cpi_gen[cpi_gen.variable == "cpi_annual_avg"]
cg = {int(x.date): x.value for x in cpi_gen.itertuples()}
rows = [{"x": y, "y": round(v, 1), "s": "Precios del joven que alquila (alquiler nuevo)"} for y, v in b_new.items()]
rows += [{"x": y, "y": round(v, 1), "s": "Ídem con el alquiler del IPC"} for y, v in b_cpi.items()]
rows += [{"x": y, "y": round(cg[y] / cg[2008] * 100, 1), "s": "IPC general"} for y in range(2008, 2026)]
rows += [{"x": y, "y": round(sal[y] / sal[2008] * 100, 1), "s": "Sueldo bruto medio de 25-34"} for y in sorted(sal) if y >= 2008]
dump("c03", rows)
last = max(y for y in sal if y >= 2008 and y in b_new)
print(f"c03 {last}: basket(new rent) {b_new[last]:.1f} | basket(CPI rent) {b_cpi[last]:.1f} | CPI {cg[last]/cg[2008]*100:.1f} | young salary {sal[last]/sal[2008]*100:.1f}")

# ---------- c05 panel extras
cpi = cg
ex = []
for y in sorted(sal):
    if y >= 2008 and y in allages:
        ex.append({"date": y, "variable": "young_rel_salary", "value": round(sal[y] / allages[y] * 100, 2), "better": "up",
                   "label": "Sueldo de 25-34 en % del sueldo medio de todas las edades (control: el resto de edades)", "source_id": "INE EES/EAES"})
for d in years_flat:
    if d["x"] >= 2002:
        ex.append({"date": d["x"], "variable": "years_flat", "value": d["y"], "better": "down",
                   "label": "Años de sueldo joven para un piso de 80 m² (sin control internacional)", "source_id": "MIVAU + INE EES"})
pd.DataFrame(ex).to_csv(os.path.join(CLEAN, "c05_panel_extra.csv"), index=False)
print("c05 panel extra rows:", len(ex))
