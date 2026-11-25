"""c02: house prices. Ministerio valor tasado (quarterly, 1995-), Vergés/INE 1987-94 annual, BdE copy.
Run: python -I scripts/c02_house_prices.py  (needs raw files in data/raw/c02)"""
import re, sys, glob, os
import pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'data', 'raw', 'c02'); OUT = os.path.join(ROOT, 'data', 'clean')
os.makedirs(OUT, exist_ok=True)
rows = []
FILES = {'35101000': ('price_m2_all', 'mivau_valor_tasado_libre'),
         '35101500': ('price_m2_le5y', 'mivau_valor_tasado_libre_le5y'),
         '35102000': ('price_m2_gt5y', 'mivau_valor_tasado_libre_gt5y')}
for code, (var, sid) in FILES.items():
    x = pd.ExcelFile(os.path.join(RAW, f'vt_{code}.xls'))
    for sh in x.sheet_names:
        d = x.parse(sh, header=None)
        hdr = None
        for i in range(len(d)):
            if any(isinstance(v, str) and re.match(r'A.o \d{4}', v.strip()) for v in d.iloc[i]):
                hdr = i; break
        colq = {}
        yr = None
        qrow = hdr + 2
        for c in range(1, d.shape[1]):
            v = d.iloc[hdr, c]
            if isinstance(v, str) and re.match(r'A.o \d{4}', v.strip()):
                yr = int(re.search(r'\d{4}', v).group()); q = 0
            if yr is None: continue
            qv = d.iloc[qrow, c]
            if isinstance(qv, str) and re.match(r'\d', qv.strip()):
                colq[c] = f'{yr}-Q{qv.strip()[0]}'
        for i in range(qrow + 1, len(d)):
            name = d.iloc[i, 1]
            if not isinstance(name, str) or name.startswith('n.r'): continue
            name = name.strip()
            for c, per in colq.items():
                val = pd.to_numeric(d.iloc[i, c], errors='coerce')
                if pd.notna(val):
                    rows.append((per, name, '', var, val, 'EUR/m2', sid))
df = pd.DataFrame(rows, columns=['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id'])
df = df.drop_duplicates(['date', 'geo', 'variable'])
df.to_csv(os.path.join(OUT, 'c02_house_price_mivau_quarterly.csv'), index=False)
print(df.groupby('variable').date.agg(['min', 'max', 'count']))

# 1987-94 annual (Verges 2012, INE Estadistica Espanola 54(179), Tabla 5; reproduces Fomento tasaciones). SECONDARY.
txt = open(os.path.join(RAW, 'ine_verges_p44.txt'), encoding='latin1').read().split('\n')
pre = []
for l in txt:
    m = re.match(r'^(Espa.a|Madrid|Catalunya|Andaluc.a|Comunitat Valenciana)\s+((?:[\d.]+\s*){8})$', l.strip())
    if m:
        name = {'Catalunya': 'Cataluña', 'Comunitat Valenciana': 'Comunidad Valenciana'}.get(m.group(1), m.group(1))
        name = 'ESPAÑA' if name.startswith('Espa') else name
        vals = [float(v.replace('.', '')) for v in m.group(2).split()]
        for y, v in zip(range(1987, 1995), vals):
            pre.append((str(y), name, '', 'price_m2_all_annual', v, 'EUR/m2', 'verges2012_fomento_tasaciones_SECONDARY'))
pdf = pd.DataFrame(pre, columns=df.columns)
pdf.to_csv(os.path.join(OUT, 'c02_house_price_1987_1994_secondary.csv'), index=False)
print(pdf[pdf.geo == 'ESPAÑA'])

# national annual spliced: 1987-94 Verges, 1995+ mean of the 4 quarters (full years only)
nat = df[(df.geo == 'TOTAL NACIONAL') & (df.variable == 'price_m2_all')].copy()
nat['year'] = nat.date.str[:4]
g = nat.groupby('year').value.agg(['mean', 'count']).reset_index()
g = g[g['count'] == 4]
out = [(r.year, 'ES', '', 'price_m2_annual_mean', round(r['mean'], 1), 'EUR/m2', 'mivau_valor_tasado_libre') for _, r in g.iterrows()]
out = [(y, 'ES', '', 'price_m2_annual_mean', v, 'EUR/m2', 'verges2012_fomento_tasaciones_SECONDARY')
       for (y, g_, _, vv, v, u, s) in pre if g_ == 'ESPAÑA'] + out
pd.DataFrame(out, columns=df.columns).to_csv(os.path.join(OUT, 'c02_house_price_national_annual.csv'), index=False)
print(pd.DataFrame(out).iloc[[0, 7, 8, -1]])
