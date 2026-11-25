"""c03: INE CPI by ECOICOP group, annual average 2002-2025, from raw JSON (data/raw/c03).
ECOICOP v1 12 groups (table 24080, base 2021 series IPC2518xx) and COICOP 2018 13 groups (table 76125, base 2025, IPC2907xx).
Plus rent subclass (table 24079 'Vivienda en alquiler', IPC292307). Run: python -I scripts/c03_cpi_groups.py"""
import json, os
import pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'data', 'raw', 'c03'); OUT = os.path.join(ROOT, 'data', 'clean')
def monthly(series, tag, unit, sid, rows):
    for s in series:
        md = {m['T3_Variable']: m for m in s['MetaData']}
        k = md.get('Grupos ECOICOP') or md.get('Rúbricas') or [m for m in s['MetaData'] if 'ECOICOP' in m['T3_Variable']][0]
        code = k['Codigo']
        df = pd.DataFrame([(x['Anyo'], int(x['T3_Periodo'][1:]), x['Valor']) for x in s['Data'] if x['T3_Periodo'].startswith('M')], columns=['y', 'm', 'v'])
        a = df.groupby('y').agg(n=('v', 'size'), v=('v', 'mean'))
        for y, r in a[a.n == 12].iterrows():
            if y <= 2025: rows.append((str(y), 'ES', f'{tag}_{code}', 'cpi_annual_avg', round(r.v, 4), unit, sid))
rows = []
d = json.load(open(os.path.join(RAW, 'ipc_24080_all.json'), encoding='utf-8'))
monthly(d, 'ecoicop1', 'index_2021=100', 'INE_24080', rows)
d = json.load(open(os.path.join(RAW, 'ipc_76125.json'), encoding='utf-8'))
monthly([s for s in d if s['Nombre'].endswith('ndice. ')], 'coicop2018', 'index_2025=100', 'INE_76125', rows)
out = pd.DataFrame(rows, columns=['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id'])
out.to_csv(os.path.join(OUT, 'c03_cpi_groups.csv'), index=False)
print(out.groupby('group').date.agg(['min', 'max', 'count']))
print(out[out.group.isin(['ecoicop1_00', 'ecoicop1_04', 'coicop2018_00', 'coicop2018_04'])].query("date in ['2002','2025']"))
