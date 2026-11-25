"""Build chart-ready JSON for the website (docs/data/*.json) from data/clean/*.csv.

Every builder reads clean CSVs, writes one JSON per chart and prints the key numbers used in
the discussion. Run: python -I scripts/build_site.py [chart ids...]
"""
import json, os, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN = os.path.join(ROOT, "data", "clean")
OUT = os.path.join(ROOT, "docs", "data")
os.makedirs(OUT, exist_ok=True)


def rd(name):
    return pd.read_csv(os.path.join(CLEAN, f"{name}.csv"), low_memory=False)


def cpi():
    d = rd("common_cpi_es")
    d = d[d.variable == "cpi_annual_avg"]
    return dict(zip(d.date.astype(int), d.value))


def real(v, y, c=None):
    c = c or cpi()
    return v * 100 / c[int(y)] if int(y) in c else None


def dump(name, obj):
    def clean(o):
        if isinstance(o, float) and o != o:
            return None
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        return o
    with open(os.path.join(OUT, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(clean(obj), f, ensure_ascii=False, separators=(",", ":"))


def rows(df, cols):
    return [dict(zip(cols, r)) for r in df[cols].itertuples(index=False)]


def series(df, label, value="value"):
    return [{"x": int(str(d)[:4]) if (len(str(d)) == 4 or str(d)[4:6] == "-Q") else str(d), "y": round(float(v), 3), "s": label}
            for d, v in zip(df.date, df[value]) if pd.notna(v)]


# ---------------------------------------------------------------- c01
def c01():
    d = rd("c01_eurostat")
    s = d[(d.variable == "share_living_with_parents") & (d.group == "Y25-34")]
    out = []
    for geo, lab in [("ES", "España"), ("NL", "Holanda"), ("EU27_2020", "Media UE")]:
        out += series(s[s.geo == geo].sort_values("date"), lab)
    extra = []
    epa = os.path.join(CLEAN, "c01_epa.csv")
    if os.path.exists(epa):
        e = pd.read_csv(epa)
        e = e[(e.group == "25-34") & (e.variable == "share_living_with_parent_any")].sort_values("date")
        extra = series(e, "España")
    age = d[d.variable == "avg_age_leaving_parental_home"]
    ages = []
    for geo, lab in [("ES", "España"), ("NL", "Holanda"), ("EU27_2020", "Media UE")]:
        ages += series(age[age.geo == geo].sort_values("date"), lab)
    dump("c01", {"share": out, "share_epa": extra, "age": ages})
    es = s[s.geo == "ES"].set_index("date").value
    a = age[age.geo == "ES"].set_index("date").value
    print(f"c01 ES 25-34 with parents: {es.index.min()} {es.iloc[0]:.1f}% | 2008 {es.get(2008):.1f}% | {es.index.max()} {es.iloc[-1]:.1f}%")
    print(f"c01 ES avg age leaving: 2000 {a[2000]} | min {a.min()} ({a.idxmin()}) | 2025 {a[2025]}")


# ---------------------------------------------------------------- c05 (unemployment, tenure)
def c05_labour():
    u = rd("c05_unemployment_annual")
    es = u[(u.geo == "ES") & (u.group == "16-24") & u.source_id.str.startswith("derived")].sort_values("date")
    es = es.groupby("date").value.mean().reset_index()
    ctrl = u[(u.geo.isin(["EU27_2020", "PT"])) & (u.group == "15-24") & (u.source_id == "eurostat_lfsa_urgan")]
    out = series(es, "España (16-24)")
    for geo, lab in [("EU27_2020", "Media UE (15-24)"), ("PT", "Portugal (15-24)")]:
        out += series(ctrl[ctrl.geo == geo].sort_values("date"), lab)
    t = rd("c05_tenure_annual")
    t = t[(t.variable == "share_employed_tenure_M0-11") & (t.group == "15-24")]
    ten = []
    for geo, lab in [("ES", "España"), ("PT", "Portugal"), ("EU27_2020", "Media UE")]:
        ten += series(t[t.geo == geo].sort_values("date"), lab)
    dump("c05_labour", {"unemp": out, "tenure": ten})
    e = es.set_index("date").value
    print(f"c05 ES youth unemp: 1977 {e[1977]:.1f} | max {e.max():.1f} ({e.idxmax()}) | 2025 {e[2025]:.1f}")


# ---------------------------------------------------------------- c08
def c08():
    g = rd("c08_gem_aps")
    keep = {"entrepreneurship_as_a_good_career_choice_rate": "Emprender es buena opción profesional",
            "fear_of_failure_rate": "El miedo a fracasar me frenaría",
            "high_status_to_successful_entrepreneurs_rate": "Los emprendedores con éxito tienen prestigio",
            "total_early_stage_entrepreneurial_activity_tea_rate": "Adultos emprendiendo ahora (TEA)"}
    names = {"ES": "España", "NL": "Holanda", "DE": "Alemania", "FR": "Francia", "IT": "Italia", "PT": "Portugal"}
    out = []
    for v, lab in keep.items():
        x = g[g.variable == v]
        for geo, n in names.items():
            for r in x[x.geo == geo].itertuples():
                out.append({"m": lab, "x": int(r.date), "y": round(r.value, 1), "s": n})
    dump("c08", out)
    for v, lab in keep.items():
        x = g[(g.variable == v) & g.geo.isin(["ES", "NL"])].pivot_table(index="date", columns="geo", values="value")
        recent = x.loc[x.index >= x.index.max() - 4].mean()
        print(f"c08 {lab}: ES {recent.get('ES', float('nan')):.1f} vs NL {recent.get('NL', float('nan')):.1f} (last 5y avg)")


# ---------------------------------------------------------------- c11
def c11():
    le = rd("c11_life_expectancy"); hx = rd("c11_health_expenditure"); am = rd("c11_avoidable_mortality")
    un = rd("c11_unmet_needs")

    def latest(df, var, extra=None):
        x = df[df.variable == var]
        if extra is not None:
            x = x[extra(x)]
        x = x.dropna(subset=["value"]).sort_values("date").groupby("geo").tail(1)
        return x.set_index("geo")[["value", "date"]]
    spend = latest(hx, "health_exp_per_capita_pps")
    life = latest(le, "life_expectancy_at_birth", lambda x: x.group == "total")
    treat = latest(am, "treatable_mortality_rate", lambda x: x.group == "total")
    wl = latest(un, "unmet_medical_wlist", lambda x: x.group == "Y_GE16")
    oop = latest(hx, "oop_share_of_health_exp")
    eu = set("AT BE BG CY CZ DE DK EE EL ES FI FR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK".split())
    pts = []
    for geo in sorted(eu & set(spend.index)):
        pts.append({"geo": geo, "spend": round(spend.value[geo]), "life": life.value.get(geo),
                    "treat": treat.value.get(geo), "wait": wl.value.get(geo), "oop": oop.value.get(geo)})
    w = un[(un.variable == "unmet_medical_wlist") & (un.group == "Y_GE16") & un.geo.isin(["ES", "NL", "EU27_2020"])]
    wts = []
    for geo, lab in [("ES", "España"), ("NL", "Holanda"), ("EU27_2020", "Media UE")]:
        wts += series(w[w.geo == geo].sort_values("date"), lab)
    dump("c11", {"points": pts, "wait_ts": wts,
                 "years": {"spend": int(spend.date["ES"]), "life": int(life.date["ES"]), "treat": int(treat.date["ES"]), "wait": int(wl.date["ES"])}})
    for geo in ["ES", "NL"]:
        p = next(p for p in pts if p["geo"] == geo)
        print(f"c11 {geo}: spend {p['spend']} PPS, life {p['life']}, treatable {p['treat']}, waitlist unmet {p['wait']}%, oop {p['oop']}%")


# ---------------------------------------------------------------- c13 spending per person
def c13_spend():
    c = rd("c13_cofog"); p = rd("c13_population_age_bands"); k = cpi()
    c = c[c.variable == "cofog_expenditure_eur_m"]
    out = []
    for geo in ["ES", "NL"]:
        cg = c[c.geo == geo].pivot_table(index="date", columns="group", values="value")
        pg = p[p.geo == geo].pivot_table(index="date", columns="group", values="value")
        for y in cg.index:
            if y not in pg.index or y not in k:
                continue
            old = (cg.loc[y, "GF1002"] + cg.loc[y, "GF1003"]) * 1e6 / pg.loc[y, "65+"]
            young = (cg.loc[y, "GF1004"] + cg.loc[y, "GF1006"] + cg.loc[y, "GF09"]) * 1e6 / pg.loc[y, "0-29"]
            out.append({"x": int(y), "geo": geo, "old": round(real(old, y, k)), "young": round(real(young, y, k)),
                        "ratio": round(old / young, 2)})
    dump("c13_spend", out)
    for geo in ["ES", "NL"]:
        r = [o for o in out if o["geo"] == geo]
        print(f"c13 {geo}: {r[0]['x']} old {r[0]['old']} young {r[0]['young']} ratio {r[0]['ratio']} | {r[-1]['x']} old {r[-1]['old']} young {r[-1]['young']} ratio {r[-1]['ratio']} (EUR2025/person; NL deflated with ES CPI)")


# ---------------------------------------------------------------- cB
def cB():
    b = rd("cB_wvs_age")
    items = {"E040_hardwork:share_1to3": "Cree que el esfuerzo trae una vida mejor (1-3 de 10)",
             "E039_competition:share_1to3": "Cree que la competencia es buena (1-3 de 10)"}
    # A170/A173 are left out: their EVS 2017 / WVS 2022 values are broken in the harvested crosstabs (<2%).
    out = []
    for v, lab in items.items():
        x = b[(b.variable == v) & b.group.isin(["<30", "50+"])]
        for r in x.itertuples():
            out.append({"m": lab, "x": int(r.date), "y": round(r.value, 1), "geo": r.geo,
                        "s": ("España" if r.geo == "ES" else "Holanda") + (" <30" if r.group == "<30" else " 50+")})
    out.sort(key=lambda o: (o["m"], o["s"], o["x"]))
    dump("cB", out)
    x = b[(b.variable == "E040_hardwork:share_1to3") & (b.group == "<30")].pivot_table(index="date", columns="geo", values="value")
    print("cB hardwork <30:", x.round(1).to_dict())


# ---------------------------------------------------------------- c05 panel (pre-registered test)
GOVS = [(1982.92, 1996.33, "PSOE", "González"), (1996.33, 2004.33, "PP", "Aznar"), (2004.33, 2011.97, "PSOE", "Zapatero"),
        (2011.97, 2018.42, "PP", "Rajoy"), (2018.42, 2030.0, "PSOE", "Sánchez")]


def gov_of(year, lag):
    t = year + 0.5 - lag
    for s, e, p, n in GOVS:
        if s <= t < e:
            return p, n
    return None, None


def slope(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else float("nan")


def panel_metrics():
    """Each metric: (key, label, gap series {year: ES - control}, better='down'|'up', note)."""
    m = []
    u = rd("c05_unemployment_annual")
    es = u[(u.geo == "ES") & (u.group == "15-24") & (u.source_id == "eurostat_lfsa_urgan")].set_index("date").value
    pt = u[(u.geo == "PT") & (u.group == "15-24") & (u.source_id == "eurostat_lfsa_urgan")].set_index("date").value
    m.append(("unemp", "Paro juvenil 15-24: España menos Portugal (puntos)", (es - pt).dropna(), "down", "Eurostat lfsa_urgan"))
    t = rd("c05_tenure_annual")
    t = t[(t.variable == "share_employed_tenure_M0-11") & (t.group == "15-24")]
    es = t[t.geo == "ES"].set_index("date").value; pt = t[t.geo == "PT"].set_index("date").value
    m.append(("tenure", "Ocupados 15-24 con < 1 año en su empleo: España menos Portugal (puntos)", (es - pt).dropna(), "down", "Eurostat lfsa_qoe"))
    d = rd("c01_eurostat")
    s = d[(d.variable == "share_living_with_parents") & (d.group == "Y25-34")]
    es = s[s.geo == "ES"].set_index("date").value; nl = s[s.geo == "NL"].set_index("date").value
    m.append(("parents", "25-34 viviendo con sus padres: España menos Holanda (puntos)", (es - nl).dropna(), "down", "Eurostat ilc_lvps08"))
    extra = os.path.join(CLEAN, "c05_panel_extra.csv")  # added later: salary, price/salary, autónomo fee
    if os.path.exists(extra):
        e = pd.read_csv(extra)
        for key, g in e.groupby("variable"):
            m.append((key, g.label.iloc[0], g.set_index("date").value, g.better.iloc[0], g.source_id.iloc[0]))
    return m


def c05_panel():
    out = {"metrics": [], "summary": {}}
    for lag in (0, 2, 4):
        consistent = []
        for key, label, gap, better, src in panel_metrics():
            per = {}
            for y, v in gap.items():
                p, n = gov_of(int(y), lag)
                if p:
                    per.setdefault((n, p), []).append((int(y), float(v)))
            rows = []
            for (n, p), pts in per.items():
                if len(pts) >= 3:
                    sl = slope([a for a, _ in pts], [b for _, b in pts])
                    imp = -sl if better == "down" else sl
                    rows.append({"gov": n, "party": p, "n": len(pts), "slope": round(sl, 3), "improve": round(imp, 3)})
            ps = [r["improve"] for r in rows if r["party"] == "PSOE"]
            pp = [r["improve"] for r in rows if r["party"] == "PP"]
            pattern = "sin patrón"
            if len(ps) >= 1 and len(pp) >= 1 and len(ps) + len(pp) >= 3:
                if min(ps) > max(pp):
                    pattern = "PSOE mejor"
                elif min(pp) > max(ps):
                    pattern = "PP mejor"
            if pattern != "sin patrón":
                consistent.append(key)
            if lag == 0:
                out["metrics"].append({"key": key, "label": label, "better": better, "src": src,
                                       "series": [{"x": int(y), "y": round(float(v), 2), "s": "España − control"} for y, v in gap.items()]})
            out["summary"].setdefault(key, {})[f"lag{lag}"] = {"rows": rows, "pattern": pattern}
        out["summary"].setdefault("_count", {})[f"lag{lag}"] = consistent
        print(f"c05 panel lag {lag}: consistent metrics {consistent}")
    for k, v in out["summary"].items():
        if k != "_count":
            print("   ", k, {l: (x["pattern"], [(r["gov"], r["improve"]) for r in x["rows"]]) for l, x in v.items() if l == "lag0"})
    dump("c05_panel", out)


# ---------------------------------------------------------------- c04
def c04():
    c = rd("c04_completions"); h = rd("c04_households")
    comp = c[c.variable == "homes_completed_total"].set_index("date").value
    vpo = c[c.variable == "homes_completed_protegidas"].set_index("date").value
    ch = h[h.variable == "households_change_yoy"].set_index("date").value
    ecp = h[h.variable == "households_change_yoy_ecp"].set_index("date").value
    form = {}
    for y, v in ch.items():
        if 2000 <= y <= 2020 and y != 2002:
            form[int(y)] = v
    for y, v in ecp.items():
        form[int(y)] = v
    out = [{"x": int(y), "y": round(v / 1000, 1), "s": "Viviendas terminadas"} for y, v in comp.items()]
    out += [{"x": y, "y": round(v / 1000, 1), "s": "Hogares nuevos"} for y, v in sorted(form.items())]
    out += [{"x": int(y), "y": round(v / 1000, 1), "s": "Protegidas (VPO)"} for y, v in vpo.items()]
    dump("c04", out)
    gap = {y: comp.get(y) - form[y] for y in form if y in comp.index}
    print("c04 completions-minus-households (k):", {y: round(g / 1000) for y, g in gap.items() if y >= 2008})
    a = sum(comp.get(y, 0) for y in range(2012, 2026)); b = sum(form.get(y, 0) for y in range(2012, 2026))
    print(f"c04 2012-2025 completions {a/1e6:.2f}M vs new households {b/1e6:.2f}M (2021 missing)")


# ---------------------------------------------------------------- c07 pilot
def c07():
    w = rd("c07_pilot_wide")
    w = w[w.pp_ran == 1]
    pts = [{"name": r.name, "year": int(r.year), "m": round(r.pp_margin_pts, 1), "d": round(r.dwellings_per1000, 2), "pop": int(r.population)}
           for r in w.itertuples() if abs(r.pp_margin_pts) <= 40]
    dump("c07", pts)
    near = w[w.pp_margin_pts.abs() <= 10]
    print("c07 within 10pts:", near.groupby([near.year, near.pp_margin_pts > 0]).dwellings_per1000.agg(["median", "count"]).round(2).to_dict())


# ---------------------------------------------------------------- c09, c12
def c09():
    k = rd("c09_cost_curve")
    k = k[k.variable == "total"]
    lab = {("ES", "standard"): "España", ("ES", "tarifa_plana_year1"): "España, 1.er año (tarifa plana)",
           ("NL", "urencriterium"): "Holanda", ("NL", "urencriterium_starter"): "Holanda, empezando (startersaftrek)"}
    out = [{"x": int(r.net_income_eur), "y": round(r.value), "s": lab[(r.geo, r.group)]}
           for r in k.itertuples() if (r.geo, r.group) in lab]
    dump("c09", out)
    for inc in (0, 6000, 12000, 24000, 48000):
        print("c09", inc, {s_: next((o["y"] for o in out if o["x"] == inc and o["s"] == s_), None) for s_ in lab.values()})


def c12():
    c = rd("c12_contributions")
    names = {"current_pensions_PAYG": "Pensiones actuales (reparto)", "reserve_or_own_pension_fund": "Tu propio fondo / reserva",
             "health_and_care": "Sanidad y dependencia", "unemployment_disability_other": "Paro, incapacidad y otros",
             "income_tax": "Impuesto sobre la renta"}
    out = []
    for geo in ["ES", "NL"]:
        g = c[c.geo == geo]
        lc = g[g.variable == "labour_cost_gross_plus_employer_contributions"].value.iloc[0]
        net = g[g.variable == "employee_net_pay_before_health_premium_adj"].value.iloc[0]
        for cat, n in names.items():
            v = g[(g.group == cat) & (g.variable == "category_total")].value
            out.append({"geo": "España" if geo == "ES" else "Holanda", "cat": n, "eur": round(float(v.iloc[0])), "pct": round(float(v.iloc[0]) / lc * 100, 1)})
        out.append({"geo": "España" if geo == "ES" else "Holanda", "cat": "Te queda neto", "eur": round(net), "pct": round(net / lc * 100, 1)})
        print("c12", geo, "labour cost", lc, [(o["cat"][:12], o["pct"]) for o in out if o["geo"].startswith("Esp" if geo == "ES" else "Hol")])
    dump("c12", out)


BUILDERS = {"c01": c01, "c04": c04, "c07": c07, "c09": c09, "c12": c12, "c05": c05_labour, "c05p": c05_panel, "c08": c08, "c11": c11, "c13": c13_spend, "cB": cB}



# ---------------------------------------------------------------- c13 votes by age (appended)
def c13_votes():
    t = rd("c13_turnout_age"); p = rd("c13_population_age_bands")
    p = p[(p.geo == "ES")].pivot_table(index="date", columns="group", values="value")
    bands = ["18-29", "30-44", "45-64", "65+"]
    out, tab = [], []
    for el in t.date.astype(str).unique():
        e = t[t.date.astype(str) == el]
        year = int(el[:4])
        w = e[e.variable == "self_reported_turnout_pct_weighted"].set_index("group").value
        u = e[e.variable == "self_reported_turnout_pct_unweighted"].set_index("group").value
        sr = w if all(b in w.index for b in bands + ["18+"]) else u
        off = e[e.variable == "official_turnout_pct"].value
        if off.empty or year not in p.index:
            continue
        k = float(off.iloc[0]) / sr["18+"]
        votes = {b: p.loc[year, b] * min(sr[b] * k, 100) / 100 for b in bands}
        tot = sum(votes.values())
        for b in bands:
            out.append({"x": year + (0.83 if el == "2019-11" else 0.3 if el == "2019-04" else 0), "y": round(votes[b] / tot * 100, 1), "s": f"Votos de {b}", "el": el,
                        "turnout": round(min(sr[b] * k, 100), 1), "pop_share": round(p.loc[year, b] / sum(p.loc[year, bb] for bb in bands) * 100, 1)})
        tab.append((el, round(sr["18-29"] * k, 1), round(sr["65+"] * k, 1)))
    dump("c13_votes", out)
    for el in ["1982", "2023"]:
        print("c13 votes", el, [(o["s"], o["y"], "turnout", o["turnout"], "pop", o["pop_share"]) for o in out if o["el"] == el])
    print("c13 rescaled turnout 18-29 vs 65+:", tab)


BUILDERS["c13v"] = c13_votes

# ---------------------------------------------------------------- c10
def c10():
    o = rd("c10_oecd_gov_employment")
    y = int(o.date.max())
    names = {"ESP": "España", "NLD": "Holanda", "OECD_AVG": "Media OCDE", "DEU": "Alemania", "FRA": "Francia", "ITA": "Italia", "PRT": "Portugal",
             "SWE": "Suecia", "DNK": "Dinamarca", "FIN": "Finlandia", "USA": "EE. UU.", "BEL": "Bélgica", "AUT": "Austria", "IRL": "Irlanda", "GRC": "Grecia", "POL": "Polonia"}
    bars = [{"geo": names[r.geo], "v": round(r.value, 1)} for r in o[o.date == y].itertuples() if r.geo in names]
    m = rd("c10_ees_public_private_micro")
    m = m[(m.date == m.date.max()) & (m.variable.isin(["median_gross_hourly_wage_ft_fullyear", "share_permanent_contract"]))]
    m[["sector", "edu", "age"]] = m.group.str.split("|", expand=True)
    edu = {"low(<=lower_secondary)": "Hasta ESO", "mid(upper_secondary+vocational)": "Bachillerato o FP", "high(university)": "Universidad"}
    pay = []
    for v in ["median_gross_hourly_wage_ft_fullyear", "share_permanent_contract"]:
        for age in ["all", "20-29"]:
            for e_, en in edu.items():
                g = m[(m.variable == v) & (m.edu == e_) & (m.age == age)].set_index("sector").value
                if "public" in g and "private" in g:
                    pay.append({"var": v, "age": age, "edu": en, "public": round(g["public"], 2), "private": round(g["private"], 2)})
    t = rd("c10_temporary_rate_sector_es")
    t = t[t.group == "16-29"].copy()
    t["year"] = t.date.str[:4].astype(int)
    tt = t.groupby(["year", "variable"]).value.mean().unstack()
    temp = [{"x": int(yr), "y": round(r.temporary_rate_public, 1), "s": "Sector público"} for yr, r in tt.iterrows()] +            [{"x": int(yr), "y": round(r.temporary_rate_private, 1), "s": "Sector privado"} for yr, r in tt.iterrows()]
    dump("c10", {"year": y, "bars": bars, "pay": pay, "temp": temp, "pay_year": int(m.date.max())})
    print("c10", y, sorted((b["v"], b["geo"]) for b in bars)[:4], "...")
    for r in pay:
        print("   ", r)
    print("   temp 16-29 last:", tt.iloc[-1].round(1).to_dict(), "first:", tt.iloc[0].round(1).to_dict())


BUILDERS["c10"] = c10


if __name__ == "__main__":
    for k in (sys.argv[1:] or BUILDERS):
        try:
            BUILDERS[k]()
        except Exception as e:  # keep building the rest
            print(f"{k} FAILED: {type(e).__name__}: {e}")
