import re,json,csv,glob,html
R='data/raw/c08/'
M={'France':'FR','Germany':'DE','Italy':'IT','Netherlands':'NL','Spain':'ES','United Kingdom':'UK','United States':'US','Portugal':'PT'}
rows=[]
for fn in sorted(glob.glob(R+'gem_*_rate.json')):
    ind=fn.split('gem_')[1][:-5]; d=json.load(open(fn,encoding='utf8',errors='replace'))
    for c,y,v in re.findall(r'data-table-country">([^<]+)</td>\s*<td class="data-table-year">(\d+)</td>\s*<td class="data-table-indicator">([^<]*)</td>',d['table']):
        v=v.strip()
        if not re.match(r'^[0-9.]+$',v): continue
        rows.append([y,M[html.unescape(c).strip()],'',ind,float(v),'percent','gem_aps_key'])
rows.sort(key=lambda r:(r[3],r[1],r[0]))
with open('data/clean/c08_gem_aps.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows))
import collections
c=collections.defaultdict(list)
for r in rows: c[(r[3],r[1])].append(r[0])
for k,v in c.items():
    if k[1] in('ES','NL'): print(k,v[0],v[-1],len(v))
