"""c09: yearly cost of being self-employed (single, <30, no children, no other income), ES vs NL, 2026 rules.
Output: data/clean/c09_cost_curve.csv (extra trailing column net_income_eur).
net_income_eur X = annual business profit BEFORE the person's own social contributions / health premium
(ES: before cuota RETA; NL: winst voor ondernemersaftrek). See sources/c09.md for every parameter."""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- Spain ----------------
# Orden PJC/297/2026 art. 18.1 (tablas): upper limit of monthly net yield, minimum base
ES_TABLE = [
    (670, 653.59), (900, 718.95), (1166.70, 849.67),  # tabla reducida tramos 1-3
    (1300, 950.98), (1500, 960.78), (1700, 960.78), (1850, 1143.79), (2030, 1209.15), (2330, 1274.51),
    (2760, 1356.21), (3190, 1437.91), (3620, 1519.61), (4050, 1601.31), (6000, 1732.03), (1e18, 1928.10)]
RATE_CC, RATE_PROF, RATE_CESE, RATE_FP, RATE_MEI = 28.30, 1.30, 0.90, 0.10, 0.90   # art. 18.2, 37.5, 37.6
RATE_TOT = (RATE_CC + RATE_PROF + RATE_CESE + RATE_FP + RATE_MEI) / 100             # 31.50 %
GENERIC_DED = 0.07                       # LGSS art. 308.1.c) regla 2.a
TARIFA_PLANA_MONTH = 80.0                # RDL 13/2022 DT 5.a (2023-25); 2026 NOT fixed by any BOE text -> assumption

def es_min_base(monthly_net):
    for lim, b in ES_TABLE:
        if monthly_net <= lim:
            return b
    return ES_TABLE[-1][1]

def es_cuota(X, flat=False):
    """annual cuota; fixed point because computable yield = X - gastos de dificil justificacion."""
    if flat:
        return TARIFA_PLANA_MONTH * 12
    cuota = 0.0
    for _ in range(8):
        dj = min(0.05 * max(X - cuota, 0), 2000)
        comp = max(X - dj, 0) * (1 - GENERIC_DED) / 12
        new = es_min_base(comp) * RATE_TOT * 12
        if abs(new - cuota) < 0.005:
            break
        cuota = new
    return cuota

STATE = [(12450, .095), (20200, .12), (35200, .15), (60000, .185), (300000, .225), (1e18, .245)]   # LIRPF art. 63
MADRID = [(13362.22, .085), (19004.63, .107), (35425.68, .128), (57320.40, .174), (1e18, .205)]    # DL 1/2010 art. 1

def scale(base, sc):
    t, lo = 0.0, 0.0
    for up, r in sc:
        if base > lo:
            t += (min(base, up) - lo) * r
        lo = up
    return t

MIN_STATE, MIN_MADRID = 5550.0, 5956.65   # LIRPF art. 57.1 ; DL 1/2010 art. 2

def es_irpf(X, cuota, starter=False):
    rn_prev = max(X - cuota, 0)
    dj = min(0.05 * rn_prev, 2000)                      # RIRPF art. 30.2.2.a
    rn = rn_prev - dj
    red = 0.0                                           # LIRPF art. 32.2.3 (rentas < 12,000)
    if rn <= 8000:
        red = 1620.0
    elif rn <= 12000:
        red = 1620 - 0.405 * (rn - 8000)
    base = max(rn - red, 0)
    if starter and base > 0:
        base *= 0.8                                     # LIRPF art. 32.3 (20 % first positive years)
    st = max(scale(base, STATE) - scale(min(base, MIN_STATE), STATE), 0)
    au = max(scale(base, MADRID) - scale(min(base, MIN_MADRID), MADRID), 0)
    return st + au, st, au

# ---------------- Netherlands ----------------
B1, B2 = 38883.0, 78426.0
R_TAX, R_AOW, R_ANW, R_WLZ = .0810, .1790, .0010, .0965
R2, R3 = .3756, .495
ZA, STARTER, MKB = 1200.0, 2123.0, 0.127
ZVW_RATE, ZVW_MAX = .0485, 79409.0
PREMIUM = 158.39 * 12                      # mean monthly premium of the 59 basic policies 2026 (Informatiekaart 2026)
ZT_STD, ZT_DREMPEL, ZT_A, ZT_B, ZT_LIMIT = 2119.0, 29736.0, .01912, .1373, 40857.0

def ahk(i):
    return max(0.0, 3115.0 - (0.06398 * (i - 29736.0) if i > 29736.0 else 0.0))

def ak(l):
    if l <= 0:
        return 0.0
    if l <= 11965:
        return .08324 * l
    if l <= 25845:
        return 996 + .31009 * (l - 11965)
    if l <= 45592:
        return 5300 + .0195 * (l - 25845)
    return max(0.0, 5685 - .0651 * (l - 45592))

def zorgtoeslag(i):
    if i > ZT_LIMIT:
        return 0.0
    norm = ZT_A * ZT_DREMPEL + ZT_B * max(0.0, i - ZT_DREMPEL)
    return max(0.0, ZT_STD - norm)

def apply_credits(comp, credit_total):
    """Heffingskorting = tax part + AOW/Anw/Wlz parts in proportion 8.10/17.90/0.10/9.65 (Wet IB 8.4-8.6 via
    Belastingdienst); each part offsets its own levy; unused tax part offsets premiums (goedkeuring)."""
    tot = R_TAX + R_AOW + R_ANW + R_WLZ
    rates = {'tax': R_TAX, 'aow': R_AOW, 'anw': R_ANW, 'wlz': R_WLZ}
    net, used, spill = {}, 0.0, 0.0
    for k in comp:
        part = credit_total * rates[k] / tot
        u = min(part, comp[k])
        net[k] = comp[k] - u
        used += u
        if k == 'tax':
            spill = part - u
    for k in ('aow', 'wlz', 'anw'):
        u = min(spill, net[k])
        net[k] -= u
        used += u
        spill -= u
    return net, used

def nl_cost(W, urencriterium=True, starter=False):
    aftrek = 0.0
    if urencriterium:
        aftrek = ZA + (STARTER if starter else 0.0)
    aftrek = min(aftrek, W)
    mkb = MKB * (W - aftrek)
    i = W - aftrek - mkb                              # taxable box-1 income
    l = W - aftrek                                    # arbeidsinkomen (assumption: before MKB)
    b1 = min(i, B1)
    comp = {'tax': R_TAX * b1 + R2 * max(0, min(i, B2) - B1) + R3 * max(0, i - B2),
            'aow': R_AOW * b1, 'anw': R_ANW * b1, 'wlz': R_WLZ * b1}
    comp, credit = apply_credits(comp, ahk(i) + ak(l))
    zvw = ZVW_RATE * min(i, ZVW_MAX)
    zt = zorgtoeslag(i)
    return dict(tax=comp['tax'], vv=comp['aow'] + comp['anw'] + comp['wlz'], zvw=zvw, premium=PREMIUM,
                zt=zt, credit=credit, taxable=i)

# ---------------- output ----------------
def main():
    rows = []

    def add(geo, scen, X, var, val, unit="EUR/year"):
        rows.append(["2026", geo, scen, var, round(val, 2), unit, "c09_cost.py", X])

    for X in range(0, 60001, 500):
        for scen, flat, starter in (("standard", False, False), ("tarifa_plana_year1", True, True)):
            c = es_cuota(X, flat)
            t, st, au = es_irpf(X, c, starter)
            add("ES", scen, X, "social_contributions", c)
            add("ES", scen, X, "income_tax", t)
            add("ES", scen, X, "income_tax_state", st)
            add("ES", scen, X, "income_tax_madrid", au)
            add("ES", scen, X, "health_premium_net", 0.0)
            add("ES", scen, X, "other", 0.0)
            add("ES", scen, X, "total", c + t)
        for scen, ur, stt in (("urencriterium", True, False), ("no_urencriterium", False, False),
                              ("urencriterium_starter", True, True)):
            r = nl_cost(X, ur, stt)
            health = r['zvw'] + r['premium'] - r['zt']
            add("NL", scen, X, "social_contributions", r['vv'])
            add("NL", scen, X, "income_tax", r['tax'])
            add("NL", scen, X, "health_premium_net", health)
            add("NL", scen, X, "other", 0.0)
            add("NL", scen, X, "total", r['vv'] + r['tax'] + health)
            add("NL", scen, X, "zvw_income_contribution", r['zvw'])
            add("NL", scen, X, "basic_premium_gross", r['premium'])
            add("NL", scen, X, "zorgtoeslag", -r['zt'])
            add("NL", scen, X, "heffingskortingen_used", -r['credit'])
    out = os.path.join(ROOT, "data", "clean", "c09_cost_curve.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "geo", "group", "variable", "value", "unit", "source_id", "net_income_eur"])
        w.writerows(rows)
    print("wrote", out, len(rows))
    for X in (0, 12000, 24000, 48000):
        for g, sc in (("ES", "standard"), ("ES", "tarifa_plana_year1"), ("NL", "urencriterium"),
                      ("NL", "no_urencriterium"), ("NL", "urencriterium_starter")):
            v = {r[3]: r[4] for r in rows if r[1] == g and r[2] == sc and r[7] == X}
            print(X, g, sc, "tot", v['total'], "soc", v['social_contributions'], "tax", v['income_tax'],
                  "health", v['health_premium_net'])

if __name__ == "__main__":
    main()
