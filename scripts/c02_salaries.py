"""c02: salaries by age. INE EES (1995, 2002, 2006 quadrennial px tables; EAES annual 2008-2024; quadrennial 2018, 2022 with medians)
and AEAT Modelo 190 mean salary by age (editions 2006-2025, parsed by c02_aeat.py).
Run: python -I -X utf8 scripts/c02_aeat.py ; python -I -X utf8 scripts/c02_salaries.py"""
import os, re, json, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _px
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'data', 'raw', 'c02'); OUT = os.path.join(ROOT, 'data', 'clean')
ESP_EUR = 166.386
rows = []
def band(s):
    s = s.replace('�', 'ñ').strip()
    m = re.search(r'(\d+) a (\d+)', s)
    if m: return f'{m.group(1)}-{m.group(2)}'
    m = re.search(r'(Menos de|Menor de) (\d+)', s)
    if m: return f'<{m.group(2)}'
    m = re.search(r'(\d+) y m', s)
    if m: return f'{m.group(1)}+'
    m = re.search(r'Mayor de (\d+)', s)
    if m: return f'>{m.group(1)}'
    return 'all' if s.lower().startswith(('todas', 'total')) else s
def add(date, g, var, val, unit, sid):
    rows.append((str(date), 'ES', g, var, val, unit, sid))
# 1995 (thousand pesetas -> EUR), both sexes
for r, v in _px.parse(os.path.join(RAW, 'ees95_01015.px')):
    k = r['Media/percentiles']
    if k in ('Media', 'Percentil 50') and v is not None:
        add(1995, band(r['Edad']), 'earn_mean_annual_gross' if k == 'Media' else 'earn_median_annual_gross', round(v * 1000 / ESP_EUR, 2), 'EUR', 'INE_EES1995_01015')
for y, f, sid in [(2002, 'ees02_01006.px', 'INE_EES2002_01006'), (2006, 'ees06_8925.px', 'INE_EES2006_8925')]:
    for r, v in _px.parse(os.path.join(RAW, f)):
        k = r['Media y percentiles']
        if r['Sexo'] == 'Ambos sexos' and k in ('Media', 'Percentil 50') and v is not None:
            add(y, band(r['Edad del trabajador']), 'earn_mean_annual_gross' if k == 'Media' else 'earn_median_annual_gross', v, 'EUR', sid)
# EAES annual mean, national, both sexes: 28201 (broad bands) and 28189 (5-year bands)
for t in (28201, 28189):
    for s in json.load(open(os.path.join(RAW, f'ees_{t}.json'), encoding='utf-8')):
        n = s['Nombre']
        if not n.startswith('Ambos sexos') or 'Total Nacional' not in n: continue
        age = n.split('. ')[1]
        for x in s['Data']:
            add(x['Anyo'], band(age), 'earn_mean_annual_gross', x['Valor'], 'EUR', f'INE_EAES_{t}')
# quadrennial 2018 / 2022: mean and median by broad age band
for t, y in ((70692, 2018), (36850, 2022)):
    for s in json.load(open(os.path.join(RAW, f'ees_{t}.json'), encoding='utf-8')):
        p = [q.strip() for q in s['Nombre'].split('. ')]
        if p[0] != 'Total Nacional' or p[2] not in ('Ambos sexos', 'Total'): continue
        k = p[4].rstrip('.')
        if k in ('Media', 'Mediana', '50'):
            for x in s['Data']:
                add(x['Anyo'], band(p[3]), 'earn_mean_annual_gross' if k == 'Media' else 'earn_median_annual_gross', x['Valor'], 'EUR', f'INE_EAES_Q_{t}')
# AEAT
a = pd.read_csv(os.path.join(RAW, 'aeat', 'aeat_age_long.csv'))
a['col'] = a.col.str.replace(r'\s+', ' ', regex=True).str.strip().str.lower()
for _, r in a.iterrows():
    var = {'salario medio anual': 'aeat_mean_salary_annual', 'asalariados': 'aeat_employees', 'percepciones por persona': 'aeat_payments_per_person', 'salarios': 'aeat_total_salaries'}[r.col]
    unit = {'aeat_mean_salary_annual': 'EUR', 'aeat_employees': 'persons', 'aeat_payments_per_person': 'count', 'aeat_total_salaries': 'EUR'}[var]
    add(r.edition, band(r.age), var, r.value, unit, 'AEAT_MTP')
df = pd.DataFrame(rows, columns=['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id']).drop_duplicates(['date', 'group', 'variable', 'source_id'])
df.to_csv(os.path.join(OUT, 'c02_salaries.csv'), index=False)
print(df.groupby(['source_id', 'variable']).agg(n=('value', 'size'), y0=('date', 'min'), y1=('date', 'max')))
print(df[(df.variable.isin(['earn_mean_annual_gross', 'earn_median_annual_gross'])) & df.group.isin(['all', '25-34', '25-29', '30-34', '<25'])].sort_values(['variable', 'group', 'date']).to_string())
