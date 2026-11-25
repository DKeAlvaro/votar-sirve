"""c02: BdE series D_TKB57110_IPV 'Precio de la vivienda / renta bruta por hogar' (years), quarterly from 1987Q1 (BdE statistical series, SI_1_5.43).
Run: python -I -X utf8 scripts/c02_bde_affordability.py"""
import os, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
d = pd.read_csv(os.path.join(ROOT, 'data', 'raw', 'c02', 'bde_si_1_5.csv'), encoding='latin1', header=None, dtype=str)
M = {'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12}
rows = []
for i in range(6, len(d)):
    lab, v = d.iloc[i, 0], d.iloc[i, 43]
    if lab[:3] in M and v not in ('_', None) and pd.notna(v):
        y = int(lab[-4:]); m = M[lab[:3]]
        rows.append((f'{y}-Q{(m - 1) // 3 + 1}', 'ES', '', 'house_price_to_gross_household_income', float(v), 'years', 'BdE_D_TKB57110_IPV'))
out = pd.DataFrame(rows, columns=['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id'])
out.to_csv(os.path.join(ROOT, 'data', 'clean', 'c02_house_price_bde_affordability.csv'), index=False)
print(out.iloc[[0, 1, -1]])
