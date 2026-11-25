"""c06 event studies (pre-registered rule): gap = affected - control; the law 'moved something'
if the average post-law gap (months 0..+36) falls outside the [min, max] range of the gap in
the 36 pre-law months. Writes docs/data/c06.json. Run: python -I scripts/build_c06.py
"""
import json, math, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "data", "clean")
rd = lambda n: pd.read_csv(os.path.join(CLEAN, f"{n}.csv"), low_memory=False)


def months(d0, k):
    y, m = map(int, d0.split("-"))
    m0 = y * 12 + (m - 1) + k
    return f"{m0 // 12}-{m0 % 12 + 1:02d}"


def evaluate(gap, t0, pre, post, step=1):
    """gap: dict date->value; dates are period labels; pre/post in periods."""
    keys = sorted(gap)
    i0 = keys.index(t0)
    pre_v = [gap[k] for k in keys[max(0, i0 - pre):i0]]
    post_v = [gap[k] for k in keys[i0:i0 + post + 1]]
    lo, hi = min(pre_v), max(pre_v)
    pm = sum(post_v) / len(post_v)
    moved = pm < lo or pm > hi
    return {"pre_min": round(lo, 3), "pre_max": round(hi, 3), "post_mean": round(pm, 3), "moved": moved,
            "n_pre": len(pre_v), "n_post": len(post_v)}


def rel(keys, t0):
    i0 = keys.index(t0)
    return {k: i - i0 for i, k in enumerate(keys)}


out = {}

# ---- E1: minimum wage +22% (Jan 2019). Youth share of affiliation, high- vs low-bite provinces.
b = rd("c06_smi_bite_province")
b = b[b.variable == "bite_index_refmedian_over_prov_median_income_per_consumption_unit"].set_index("geo").value
q = b.quantile([1 / 3, 2 / 3])
high, low = set(b[b >= q.iloc[1]].index), set(b[b <= q.iloc[0]].index)
p = rd("c06_ss_province_age")
p = p[p.geo.isin(high | low)]
p["young"] = p.group.isin(["16-19", "20-24"])
tot = p[p.group == "total"].groupby(["date", p.geo.isin(high)]).value.sum().unstack()
yng = p[p.young].groupby(["date", p.geo.isin(high)]).value.sum().unstack()
share = (yng / tot * 100)
share = share[(share.index >= "2016-01") & (share.index <= "2022-01")]
gap = (share[True] - share[False]).to_dict()
t0 = "2019-01"
ev = evaluate(gap, t0, 36, 36)
ev_precovid = evaluate(gap, t0, 36, 13)
keys = sorted(gap); r = rel(keys, t0)
out["smi"] = {
    "title": "Subida del SMI de 2019 (+22%)", "t0": t0, "unit": "puntos",
    "lines": [{"x": r[k], "y": round(share.loc[k, True], 3), "s": "Provincias donde el SMI pesa más"} for k in keys] +
             [{"x": r[k], "y": round(share.loc[k, False], 3), "s": "Provincias donde pesa menos"} for k in keys],
    "gap": [{"x": r[k], "y": round(v, 3), "s": "Diferencia"} for k, v in sorted(gap.items())],
    "y": "% de afiliados que tiene 16-24 años", "eval": ev, "eval_precovid": ev_precovid,
    "groups": {"high": sorted(high), "low": sorted(low)},
}
print("E1 SMI:", ev, "| pre-covid (0..+13):", ev_precovid)

# ---- E2: labour reform (temporary contracts restricted from 2022-04). Real stability vs contract label.
t = rd("c06_tenure_quarterly")
t = t[(t.variable == "share_employed_tenure_lt3m") & (t.group == "15-24")].pivot_table(index="date", columns="geo", values="value")
t = t[(t.index >= "2019-Q2") & (t.index <= "2025-Q2")]
gap2 = (t["ES"] - t["PT"]).dropna().to_dict()
t0q = "2022-Q2"
ev2 = evaluate(gap2, t0q, 12, 12)
keys = sorted(gap2); r = rel(keys, t0q)
c = rd("c06_ss_rg_contract_age")
c = c[c.group.isin(["16-19", "20-24", "25-29"])].groupby(["date", "variable"]).value.sum().unstack()
indef = (c[["affiliates_rg_indefinido_t_completo", "affiliates_rg_indefinido_t_parcial", "affiliates_rg_indefinido_fijos_discontinuos"]].sum(axis=1)
         / c["affiliates_rg_todas_las_modalidades_de_contratos"] * 100)
indef = indef[(indef.index >= "2019-04") & (indef.index <= "2025-04")]
ki = sorted(indef.index); ri = rel(ki, "2022-04")
out["reform"] = {
    "title": "Reforma laboral (contratos temporales limitados desde abril de 2022)", "t0": t0q, "unit": "puntos",
    "lines": [{"x": r[k] * 3, "y": round(t.loc[k, "ES"], 2), "s": "España"} for k in keys] +
             [{"x": r[k] * 3, "y": round(t.loc[k, "PT"], 2), "s": "Portugal"} for k in keys],
    "label": [{"x": ri[k], "y": round(v, 2), "s": "Menores de 30 con contrato indefinido"} for k, v in indef.items()],
    "gap": [{"x": r[k] * 3, "y": round(v, 2), "s": "Diferencia"} for k, v in sorted(gap2.items())],
    "y": "% de ocupados 15-24 que lleva menos de 3 meses en su empleo", "eval": ev2,
}
print("E2 reform tenure<3m ES-PT:", ev2, "| indefinite <30:", round(indef.iloc[0], 1), "->", round(indef.iloc[-1], 1))

# ---- E3: autónomo fee reform (Jan 2023). RETA affiliates under 30 vs 30-44, log index.
a = rd("c06_ss_affiliation_age_regime")
a = a[a.variable == "affiliates_avg_reg_esp_autonomos"]
yy = a[a.group.isin(["16-19", "20-24", "25-29"])].groupby("date").value.sum()
oo = a[a.group.isin(["30-34", "35-39", "40-44"])].groupby("date").value.sum()
win = (yy.index >= "2020-01") & (yy.index <= "2025-12")
yy, oo = yy[win], oo[win]
t0m = "2023-01"
iy, io = yy / yy[months(t0m, -1)] * 100, oo / oo[months(t0m, -1)] * 100
gap3 = {k: math.log(iy[k] / io[k]) * 100 for k in iy.index}
ev3 = evaluate(gap3, t0m, 36, 35)
keys = sorted(gap3); r = rel(keys, t0m)
out["reta"] = {
    "title": "Cuotas de autónomos por ingresos (enero de 2023)", "t0": t0m, "unit": "%",
    "lines": [{"x": r[k], "y": round(iy[k], 2), "s": "Autónomos menores de 30"} for k in keys] +
             [{"x": r[k], "y": round(io[k], 2), "s": "Autónomos de 30-44"} for k in keys],
    "y": "Índice, diciembre de 2022 = 100", "eval": ev3,
    "gap": [{"x": r[k], "y": round(v, 2), "s": "Diferencia"} for k, v in sorted(gap3.items())],
}
print("E3 RETA <30 vs 30-44:", ev3, "| <30 level", int(yy.iloc[0]), "->", int(yy.iloc[-1]))

os.makedirs(os.path.join(ROOT, "docs", "data"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, "docs", "data", "c06.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
