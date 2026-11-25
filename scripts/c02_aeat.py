"""c02: AEAT 'Mercado de trabajo y pensiones en las fuentes tributarias' (Modelo 190): employees, salary by age band.
Crawls each edition's pages (data/raw/c02/aeat/), parses the table 'por ... edad, sexo' (Total sex, Total nationality).
Run: python -I scripts/c02_aeat.py [crawl|parse]"""
import re, os, sys, html, requests
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(ROOT, 'data', 'raw', 'c02', 'aeat')
B = 'https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/mercado/'
def get(url, fn):
    p = os.path.join(RAW, fn)
    if os.path.exists(p) and os.path.getsize(p) > 500: return open(p, encoding='utf-8', errors='replace').read()
    r = requests.get(url, timeout=20); r.encoding = 'utf-8'
    open(p, 'w', encoding='utf-8').write(r.text); return r.text
def titles(t):
    return [(m.group(1), html.unescape(re.sub('<[^>]+>', '', m.group(2))).strip()) for m in re.finditer(r'<a href="(jrubik\w+\.html)"[^>]*>(.*?)</a>', t, re.S)]
def pick(m):
    c = [(f, t) for f, t in titles(m) if 'alariado' in t and ('nacionalidad, edad' in t or 'por edad y sexo' in t)
         and 'tramos' not in t and 'Comunidad' not in t and 'provincia' not in t and 'sector' not in t]
    return c[0]
def cells(tbl):
    out = []
    for tr in re.findall(r'<tr>(.*?)</tr>', tbl, re.S):
        r = [html.unescape(re.sub('<[^>]+>', '', x)).strip() for x in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.S)]
        if r: out.append(r)
    return out
def num(x):
    x = x.replace('.', '').replace(',', '.').replace('%', '').strip()
    try: return float(x)
    except ValueError: return None
if __name__ == '__main__':
    import csv
    rows = []
    for y in range(2006, 2026):
        h = get(B + f'{y}/home.html', f'home_{y}.html')
        mp = re.search(r'href="(mapa\w+\.html)"', h).group(1)
        m = get(B + f'{y}/{mp}', f'mapa_{y}.html')
        f, t = pick(m)
        p = get(B + f'{y}/{f}', f'age_{y}.html')
        ej = re.search(r'Ejercicio (\d{4})', p)
        tb = re.search(r'<table id="table01"[^>]*>(.*?)</table>', p, re.S).group(1)
        c = cells(tb); hdr = c[0]
        print(y, ej.group(1) if ej else None, hdr, len(c))
        for r in c[1:]:
            for j in range(1, len(r)):
                v = num(r[j])
                if v is not None: rows.append((y, r[0], re.sub(r'\s+', ' ', hdr[j - 1] if len(hdr) == len(r) - 1 else hdr[j]), v))
    with open(os.path.join(RAW, 'aeat_age_long.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['edition', 'age', 'col', 'value']); w.writerows(rows)
