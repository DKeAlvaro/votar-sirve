"""c12: where do the contributions of an employee on 30,000 EUR gross (2026) go? ES (Madrid) vs NL (ABP).
Single, <30, no children, indefinite full-time contract. Output: data/clean/c12_contributions.csv
Every parameter is documented in sources/c12.md."""
import csv, os, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("c09_cost", os.path.join(ROOT, "scripts", "c09_cost.py"))
c09 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c09)

G = 30000.0
PAYG, RESERVE, HEALTH, OTHER, TAX = ("current_pensions_PAYG", "reserve_or_own_pension_fund",
                                     "health_and_care", "unemployment_disability_other", "income_tax")
items = []   # (geo, side, item, category, amount)

def add(geo, side, item, cat, amt):
    items.append((geo, side, item, cat, amt))

# ---------------- Spain ----------------
# Orden PJC/297/2026 art. 15 (CC), 16 (MEI), 33 (desempleo/FOGASA/FP), LGSS DA 61 (AT/EP, CNAE 62 total 1.50)
base = min(G, 5101.20 * 12)
es = [("employer", "contingencias_comunes", PAYG, 23.60), ("employee", "contingencias_comunes", PAYG, 4.70),
      ("employer", "MEI", RESERVE, 0.75), ("employee", "MEI", RESERVE, 0.15),
      ("employer", "desempleo", OTHER, 5.50), ("employee", "desempleo", OTHER, 1.55),
      ("employer", "FOGASA", OTHER, 0.20),
      ("employer", "formacion_profesional", OTHER, 0.60), ("employee", "formacion_profesional", OTHER, 0.10),
      ("employer", "AT_EP_cnae62", OTHER, 1.50)]
ss_emp = 0.0
for side, it, cat, r in es:
    add("ES", side, it, cat, base * r / 100)
    if side == "employee":
        ss_emp += base * r / 100
rn = G - ss_emp - 2000.0                                   # LIRPF art. 19.2.f otros gastos 2,000; art. 20 n/a (>19,747.5)
st = max(c09.scale(rn, c09.STATE) - c09.scale(min(rn, c09.MIN_STATE), c09.STATE), 0)
au = max(c09.scale(rn, c09.MADRID) - c09.scale(min(rn, c09.MIN_MADRID), c09.MADRID), 0)
add("ES", "employee", "IRPF_state", TAX, st)
add("ES", "employee", "IRPF_madrid", TAX, au)

# ---------------- Netherlands ----------------
FR_PREM, PREM_ER, PREM_EE = 19200.0, 0.1897, 0.0813         # ABP OPNP 27.1 % (2026), franchise 19,200
AP_FR, AP_ER, AP_EE = 29700.0, 0.0049, 0.0021               # ABP AP, sector Rijk 0.7 total split 0.49/0.21
pens_er = PREM_ER * (G - FR_PREM)
pens_ee = PREM_EE * (G - FR_PREM)
ap_er = AP_ER * max(G - AP_FR, 0)
ap_ee = AP_EE * max(G - AP_FR, 0)
add("NL", "employer", "ABP_OPNP_pension_premium", RESERVE, pens_er)
add("NL", "employee", "ABP_OPNP_pension_premium", RESERVE, pens_ee)
add("NL", "employer", "ABP_AP_disability_pension", OTHER, ap_er)
add("NL", "employee", "ABP_AP_disability_pension", OTHER, ap_ee)
taxable = G - pens_ee - ap_ee                                # premium deductible from loon
b1 = min(taxable, c09.B1)
comp = {'tax': c09.R_TAX * b1 + c09.R2 * max(0, min(taxable, c09.B2) - c09.B1) + c09.R3 * max(0, taxable - c09.B2),
        'aow': c09.R_AOW * b1, 'anw': c09.R_ANW * b1, 'wlz': c09.R_WLZ * b1}
net, used = c09.apply_credits(comp, c09.ahk(taxable) + c09.ak(taxable))
add("NL", "employee", "AOW_premium_net_of_credit", PAYG, net['aow'])
add("NL", "employee", "Anw_premium_net_of_credit", OTHER, net['anw'])
add("NL", "employee", "Wlz_premium_net_of_credit", HEALTH, net['wlz'])
add("NL", "employee", "income_tax_box1_net_of_credit", TAX, net['tax'])
mx = 79409.0
add("NL", "employer", "AWf_WW_low", OTHER, 0.0274 * min(G, mx))
add("NL", "employer", "AOF_WIA_small_employer_incl_Wko", OTHER, (0.0627 + 0.0050) * min(G, mx))
add("NL", "employer", "Zvw_werkgeversheffing", HEALTH, 0.0610 * min(G, mx))
zt = c09.zorgtoeslag(taxable)
add("NL", "employee", "basic_health_premium_gross", HEALTH, c09.PREMIUM)
add("NL", "employee", "zorgtoeslag", HEALTH, -zt)

# ---------------- output ----------------
rows = []
for geo in ("ES", "NL"):
    sub = [x for x in items if x[0] == geo]
    labour_cost = G + sum(a for g, s, i, c, a in sub if s == "employer")
    for g, s, i, c, a in sub:
        rows.append(["2026", geo, c, f"{s}:{i}", round(a, 2), "EUR/year", "c12_contrib.py"])
    for cat in (PAYG, RESERVE, HEALTH, OTHER, TAX):
        tot = sum(a for g, s, i, c, a in sub if c == cat)
        er = sum(a for g, s, i, c, a in sub if c == cat and s == "employer")
        rows.append(["2026", geo, cat, "category_total", round(tot, 2), "EUR/year", "c12_contrib.py"])
        rows.append(["2026", geo, cat, "category_employer_side", round(er, 2), "EUR/year", "c12_contrib.py"])
        rows.append(["2026", geo, cat, "category_employee_side", round(tot - er, 2), "EUR/year", "c12_contrib.py"])
        rows.append(["2026", geo, cat, "share_of_labour_cost", round(100 * tot / labour_cost, 2), "pct", "c12_contrib.py"])
        rows.append(["2026", geo, cat, "share_of_gross", round(100 * tot / G, 2), "pct", "c12_contrib.py"])
    if geo == "NL":   # sensitivity: before heffingskortingen (credits are financed from general taxes)
        gross_aow, gross_tax = comp['aow'], comp['tax']
        for nm, v in (("memo_AOW_premium_before_credit", gross_aow), ("memo_income_tax_before_credit", gross_tax),
                      ("memo_heffingskortingen_used", used)):
            rows.append(["2026", geo, "memo", nm, round(v, 2), "EUR/year", "c12_contrib.py"])
            rows.append(["2026", geo, "memo", nm + "_share_of_labour_cost", round(100 * v / labour_cost, 2), "pct", "c12_contrib.py"])
    rows.append(["2026", geo, "", "labour_cost_gross_plus_employer_contributions", round(labour_cost, 2), "EUR/year", "c12_contrib.py"])
    rows.append(["2026", geo, "", "employee_net_pay_before_health_premium_adj", round(G - sum(a for g, s, i, c, a in sub if s == "employee"), 2), "EUR/year", "c12_contrib.py"])
out = os.path.join(ROOT, "data", "clean", "c12_contributions.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "geo", "group", "variable", "value", "unit", "source_id"])
    w.writerows(rows)
print("wrote", out, len(rows))
for r in rows:
    if r[3] in ("category_total", "share_of_labour_cost", "share_of_gross", "labour_cost_gross_plus_employer_contributions"):
        print(r[1], r[2], r[3], r[4])
