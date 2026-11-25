"""c02: rents. (1) INE CPI rent subclass, 1976-2025 (chained), (2) INE IPVA, (3) Ministerio SERPAVI EUR/m2, (4) INCASOL deposits Catalonia.
Run: python -I -X utf8 scripts/c02_rents.py   (raw in data/raw/c02: ipc_24079.csv, ipcb_{183,187,195}.csv, ipva_*.json, serpavi_2011_2024.xlsx, incasol_*.json)"""
import os, json
import pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'data', 'raw', 'c02'); OUT = os.path.join(ROOT, 'data', 'clean')
rows = []
def add(date, geo, group, var, val, unit, sid): rows.append((str(date), geo, group, var, val, unit, sid))
def rd(f):
    d = pd.read_csv(os.path.join(RAW, f), sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
    return d
# ---- (1) CPI rent chain
def tab(f, kind):
    d = rd(f); d.columns = [c for c in ['rub', 'tipo', 'per', 'val']]; d = d[d.tipo == kind]
    d = d[d.rub.str.contains('lquiler') & d.val.notna() & (d.val != '')]
    return {(int(p[:4]), int(p[5:])): float(v.replace(',', '.')) for p, v in zip(d.per, d.val)}
cur = pd.read_csv(os.path.join(RAW, 'ipc_24079.csv'), sep=';', encoding='utf-8-sig', decimal=',', dtype=str)
cur.columns = ['geo', 'tipo', 'rub', 'per', 'val']; cur = cur[cur.val.notna() & (cur.val != '')]
L = {(int(p[:4]), int(p[5:])): float(v.replace(',', '.')) for p, v in zip(cur.per, cur.val)}      # base 2011 index, 2002M01-
yoy = {}
for f, lo, hi in [('ipcb_195.csv', (1977, 1), (1985, 7)), ('ipcb_187.csv', (1985, 8), (2001, 12)), ('ipcb_183.csv', (2002, 1), (2002, 12))]:
    for k, v in tab(f, 'Variación anual').items():
        if lo <= k <= hi: yoy[k] = v
for y in range(1976, 2002):
    for m in range(1, 13):
        k = (y, m)
        if k not in L and (y + 1, m) in L and (y + 1, m) in yoy: L[k] = L[(y + 1, m)] / (1 + yoy[(y + 1, m)] / 100)
    if y + 1 < 2002: pass
# fill iteratively backward
for y in range(2001, 1975, -1):
    for m in range(1, 13):
        k = (y, m)
        if k not in L and (y + 1, m) in L and (y + 1, m) in yoy: L[k] = L[(y + 1, m)] / (1 + yoy[(y + 1, m)] / 100)
ser = pd.Series(L).sort_index()
ann = {y: ser[y].mean() for y in range(1976, 2026) if y in ser.index.get_level_values(0) and len(ser[y]) == 12}
base = ann[2025]
for y, v in ann.items(): add(y, 'ES', '', 'cpi_rent_annual_avg', round(100 * v / base, 4), 'index_2025=100', 'INE_CPI_rent_chain')
for (y, m), v in ser.items():
    if y >= 2002: add(f'{y}-{m:02d}', 'ES', '', 'cpi_rent_monthly', round(100 * v / base, 4), 'index_2025=100', 'INE_CPI_rent_chain')
# ---- (2) IPVA
for t in (59056, 59004):
    for s in json.load(open(os.path.join(RAW, f'ipva_{t}.json'), encoding='utf-8')):
        n = [x.strip() for x in s['Nombre'].split('. ')]
        if n[0] != 'Total Nacional': continue
        if t == 59056 and n[1] != 'Total': continue
        if t == 59004 and n[1] == 'Total': continue
        lab = '. '.join(n[1:]).rstrip('.').lower()
        var = 'ipva_' + ('index' if 'ndice' in lab and 'riaci' not in lab else 'yoy_pct')
        grp = 'new_contract' if 'Nuevo' in lab or 'nuevo' in lab else 'existing_contract' if 'xistente' in lab else 'all'
        for x in s['Data']:
            add(x['Anyo'], 'ES', grp, var, x['Valor'], 'index_2015=100' if var.endswith('index') else 'pct', f'INE_IPVA_{t}')
# ---- (3) SERPAVI
x = pd.read_excel(os.path.join(RAW, 'serpavi_2011_2024.xlsx'), sheet_name='CCAA', dtype={'CCAA': str})
for yy in range(11, 25):
    w = x[f'BI_ALVHEPCO_TVC_{yy}']
    for _, r in x.iterrows():
        for col, var, unit in [(f'ALQM2_LV_M_VC_{yy}', 'serpavi_rent_m2_median_apartment', 'EUR/m2/month'), (f'ALQM2_LV_25_VC_{yy}', 'serpavi_rent_m2_p25_apartment', 'EUR/m2/month'),
                               (f'ALQM2_LV_75_VC_{yy}', 'serpavi_rent_m2_p75_apartment', 'EUR/m2/month'), (f'ALQTBID12_M_VC_{yy}', 'serpavi_rent_month_median_apartment', 'EUR/month'),
                               (f'BI_ALVHEPCO_TVC_{yy}', 'serpavi_n_rented_apartments', 'count')]:
            if pd.notna(r[col]): add(2000 + yy, r['LITCCAA'], '', var, round(float(r[col]), 3), unit, 'MIVAU_SERPAVI_2011_2024')
    for col, var, unit in [(f'ALQM2_LV_M_VC_{yy}', 'serpavi_rent_m2_median_apartment', 'EUR/m2/month'), (f'ALQTBID12_M_VC_{yy}', 'serpavi_rent_month_median_apartment', 'EUR/month')]:
        ok = x[col].notna() & w.notna()
        if ok.any(): add(2000 + yy, 'ES', 'weighted_mean_of_CCAA_medians', var + '_national_approx', round((x.loc[ok, col] * w[ok]).sum() / w[ok].sum(), 3), unit, 'MIVAU_SERPAVI_2011_2024')
# ---- (4) INCASOL
per = {'gener-desembre': 'Y', 'gener-març': 'Q1', 'abril-juny': 'Q2', 'juliol-setembre': 'Q3', 'octubre-desembre': 'Q4', 'gener-juny': 'H1', 'gener-setembre': '9M'}
for f, geo in [('incasol_cat.json', 'Catalunya'), ('incasol_bcn.json', 'Barcelona')]:
    for r in json.load(open(os.path.join(RAW, f), encoding='utf-8')):
        p = per[r['periode']]
        if p in ('H1', '9M'): continue
        d = r['any'] if p == 'Y' else f"{r['any']}-{p}"
        add(d, geo, '', 'incasol_new_contract_rent_mean', float(r['renda']), 'EUR/month', 'INCASOL_hepw33ik_qww9bvhh')
        add(d, geo, '', 'incasol_new_contracts_n', float(r['habitatges']), 'count', 'INCASOL_hepw33ik_qww9bvhh')
df = pd.DataFrame(rows, columns=['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id'])
df.to_csv(os.path.join(OUT, 'c02_rents.csv'), index=False)
print(df.groupby(['source_id', 'variable']).agg(n=('value', 'size'), d0=('date', 'min'), d1=('date', 'max')).to_string())
a = df[df.variable == 'cpi_rent_annual_avg']; print(a.iloc[[0, 1, 10, 25, 26, -1]][['date', 'value']])
print(df[(df.variable.str.contains('national_approx|incasol_new_contract_rent_mean|ipva_index')) & df.date.isin(['2011', '2015', '2024', '2005', '2025'])].to_string())
