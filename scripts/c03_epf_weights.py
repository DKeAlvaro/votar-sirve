"""c03: expenditure shares of young (<35) renting households from INE EPF microdata.
Usage: python -I scripts/c03_epf_weights.py <year>   (2008, 2013, 2019, 2025); writes data/work/c03_w_<year>.csv
Then python -I scripts/c03_epf_weights.py merge  -> data/clean/c03_weights.csv
Shares = sum(GASTO in group)/sum(GASTO total) over households (GASTO is already grossed up by INE).
Households with reference person (sustentador principal) age <35 and REGTEN in (3 market rent, 4 reduced rent).
"""
import sys, os, zipfile, tempfile, glob, shutil
_TMP = []
import pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'data', 'raw', 'c03', 'epf'); WORK = os.path.join(ROOT, 'data', 'work'); OUT = os.path.join(ROOT, 'data', 'clean')
os.makedirs(WORK, exist_ok=True)

def load(year):
    if year == 2008:
        d = os.path.join(RAW, 'x_epf_2008', 'd')
        h = pd.read_fwf(os.path.join(d, 'Fichero de usuario de hogar a2008'), colspecs=[(4, 9), (17, 28), (28, 30), (97, 99), (154, 155)],
                        names=['NUMERO', 'FACTOR', 'NMIEMB', 'EDADSP', 'REGTEN'], dtype=str, header=None)
        g = pd.read_fwf(os.path.join(d, 'Fichero de usuario de gastos a2008'), colspecs=[(4, 9), (9, 14), (14, 29)],
                        names=['NUMERO', 'CODIGO', 'GASTO'], dtype=str, header=None)
        g['GASTO'] = g.GASTO.astype(float) / 100
    elif year == 2013:
        t = tempfile.mkdtemp(); _TMP.append(t)
        zipfile.ZipFile(os.path.join(RAW, 'x_epf_2013', 'epf_2013_datos.zip')).extract('datos_epf2013.zip', t)
        zipfile.ZipFile(os.path.join(t, 'datos_epf2013.zip')).extractall(t)
        h = pd.read_fwf(os.path.join(t, 'Fichero de usuario de hogar a2013'), colspecs=[(4, 9), (17, 28), (28, 30), (117, 119), (188, 189)],
                        names=['NUMERO', 'FACTOR', 'NMIEMB', 'EDADSP', 'REGTEN'], dtype=str, header=None)
        g = pd.read_fwf(os.path.join(t, 'Fichero de usuario de gastos a2013'), colspecs=[(4, 9), (9, 14), (14, 29)],
                        names=['NUMERO', 'CODIGO', 'GASTO'], dtype=str, header=None)
        g['GASTO'] = g.GASTO.astype(float) / 100
    else:
        z = zipfile.ZipFile(os.path.join(RAW, f'datos_{year}.zip'))
        t = tempfile.mkdtemp(); _TMP.append(t)
        for n in z.namelist():
            if n.endswith('.zip') and ('hogar' in n.lower() and 'mhogar' not in n.lower() or 'gastos' in n.lower()):
                z.extract(n, t); zipfile.ZipFile(os.path.join(t, n)).extractall(t)
        hp = glob.glob(os.path.join(t, 'md_EPF*hogar*.parquet'))[0]; gp = glob.glob(os.path.join(t, 'md_EPF*gastos*.parquet'))[0]
        h = pd.read_parquet(hp, columns=['NUMERO', 'FACTOR', 'NMIEMB', 'EDADSP', 'REGTEN'])
        g = pd.read_parquet(gp, columns=['NUMERO', 'CODIGO', 'GASTO'])
        g['GASTO'] = g.GASTO.astype(float)
        if year == 2019: g['GASTO'] /= 100   # 2019 parquet keeps 2 implied decimals
    h['EDADSP'] = pd.to_numeric(h.EDADSP); h['FACTOR'] = pd.to_numeric(h.FACTOR)
    if year < 2019: h['FACTOR'] /= 1e6
    if year == 2019: h['FACTOR'] /= 1e6
    return h, g

def run(year):
    h, g = load(year)
    print(year, len(h), len(g), g.GASTO.sum() / 1e9, 'bn EUR total'); sys.stdout.flush()
    g['grp'] = g.CODIGO.str[:2]
    g['rent'] = g.CODIGO.str.startswith('0411')
    g['imput'] = g.CODIGO.str.startswith('0421')
    pv = g.pivot_table(index='NUMERO', columns='grp', values='GASTO', aggfunc='sum', fill_value=0)
    pv['rent'] = g[g.rent].groupby('NUMERO').GASTO.sum(); pv['imputed_rent'] = g[g.imput].groupby('NUMERO').GASTO.sum()
    pv = pv.fillna(0).reset_index()
    h = h.merge(pv, on='NUMERO', how='left').fillna(0)
    grps = [c for c in pv.columns if c.isdigit()]
    rows = []
    sel = {'young_renter': (h.EDADSP < 35) & h.REGTEN.isin(['3', '4']),
           'young_all': h.EDADSP < 35,
           'all_renter': h.REGTEN.isin(['3', '4']),
           'all_households': h.EDADSP > 0}
    for name, m in sel.items():
        s = h[m]; tot = s[grps].sum().sum()
        for c in grps + ['rent', 'imputed_rent']:
            rows.append((str(year), 'ES', name, 'share_' + (('ecoicop_' + c) if c.isdigit() else c), 100 * s[c].sum() / tot, 'pct_of_total_spending', f'INE_EPF_{year}'))
        rows.append((str(year), 'ES', name, 'n_households_sample', len(s), 'count', f'INE_EPF_{year}'))
    pd.DataFrame(rows, columns=['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id']).to_csv(os.path.join(WORK, f'c03_w_{year}.csv'), index=False)
    print(h.groupby('REGTEN').apply(lambda s: pd.Series({'n': len(s), 'rent_share': s.rent.sum() / s[grps].sum().sum() * 100})))

if __name__ == '__main__':
    if sys.argv[1] == 'merge':
        df = pd.concat([pd.read_csv(f, dtype={'date': str}) for f in sorted(glob.glob(os.path.join(WORK, 'c03_w_*.csv')))])
        df.to_csv(os.path.join(OUT, 'c03_weights.csv'), index=False); print(df.shape)
    else:
        try: run(int(sys.argv[1]))
        finally:
            [shutil.rmtree(t, ignore_errors=True) for t in _TMP]
