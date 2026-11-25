"""Spanish CPI (INE), monthly 1962-latest and annual averages, rebased 2025 = 100.

Levels: INE series IPC290751 (national general index, available 2002-01 onward via API).
Before 2002: back-chained with INE IPC290750 (12-month variation, %, since 1962):
L(m-12) = L(m) / (1 + yoy(m)/100). One rounding step per year, not per month.
Usage: python -I scripts/common_cpi.py data/raw/common data/clean
"""
import json, sys, csv, urllib.request
raw, out = sys.argv[1], sys.argv[2]
def get(url, path):
    with urllib.request.urlopen(url, timeout=25) as r: open(path, 'wb').write(r.read())
    return json.load(open(path, encoding='utf-8'))
lv = get('https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/IPC290751?date=20020101:20301231', f'{raw}/ine_ipc290751.json')['Data']
yy = get('https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/IPC290750?date=19600101:20301231', f'{raw}/ine_ipc290750.json')['Data']
L = {(r['Anyo'], r['FK_Periodo']): r['Valor'] for r in lv}
Y = {(r['Anyo'], r['FK_Periodo']): r['Valor'] for r in yy}
for y in range(2001, 1961, -1):
    for m in range(1, 13):
        if (y + 1, m) in L and (y + 1, m) in Y:
            L[(y, m)] = L[(y + 1, m)] / (1 + Y[(y + 1, m)] / 100)
ann = {}
for (y, m), v in L.items(): ann.setdefault(y, []).append(v)
ann = {y: sum(v) / 12 for y, v in ann.items() if len(v) == 12}
base = ann[2025]
with open(f'{out}/common_cpi_es.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'geo', 'group', 'variable', 'value', 'unit', 'source_id'])
    for y in sorted(ann): w.writerow([y, 'ES', '', 'cpi_annual_avg', round(ann[y] / base * 100, 4), 'index_2025=100', 'INE_IPC290751_290750'])
    for (y, m) in sorted(L): w.writerow([f'{y}-{m:02d}', 'ES', '', 'cpi_monthly', round(L[(y, m)] / base * 100, 4), 'index_2025=100', 'INE_IPC290751_290750'])
print('years', min(ann), max(ann), '| 1980', round(ann[1980] / base * 100, 2), '| 2002', round(ann[2002] / base * 100, 2), '| last month', max(L), round(L[max(L)] / base * 100, 2))
