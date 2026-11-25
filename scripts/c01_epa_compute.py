"""Share of people aged 25-29 / 30-34 / 25-34 living with a parent, from INE EPA public microdata, Q2 each year.
Input: data/raw/c01/epa_q2/datos_2tYY.zip (download with c01_epa_download.sh).
  1999-2004: fixed-width (EDAD5 pos 16-17, RELPP1 18, SEXO1 19, NPADRE 22-23, NMADRE 24-25, FACTOREL 170-176 with 2 implied decimals)
  2005-2025: tab-separated CSV/.tab with header (same variable names).
Level 1 records only (people 16+). Measures:
  rel3   = RELPP1==3 (son/daughter of the reference person)
  parent = RELPP1==3 OR NPADRE/NMADRE filled (a parent is in the household; broader, census-like)
Writes data/clean/c01_epa.csv (tidy) and per-year json in data/raw/c01/epa_results/ (cache; delete to recompute).
Usage: python -I scripts/c01_epa_compute.py [year ...]
"""
import sys,os,zipfile,json,collections,io
import pandas as pd
RAW='data/raw/c01/epa_q2/';OUT='data/raw/c01/epa_results/';os.makedirs(OUT,exist_ok=True)
yrs=[int(a) for a in sys.argv[1:]] or list(range(1999,2026))
def nz(v): return v.notna()&(v.astype(str).str.strip().isin(['','0','00','nan'])==False)
def load(y):
    z=zipfile.ZipFile(RAW+f'datos_2t{y%100:02d}.zip')
    if y<=2004:
        n=[x for x in z.namelist() if not x.endswith('/')][0]
        d=pd.read_fwf(z.open(n),colspecs=[(0,3),(12,13),(15,17),(17,18),(18,19),(21,23),(23,25),(169,176)],
            names=['CICLO','NIVEL','EDAD5','RELPP1','SEXO1','NPADRE','NMADRE','FACTOREL'],dtype=str,header=None)
        d['FACTOREL']=pd.to_numeric(d.FACTOREL,errors='coerce')/100
    else:
        n=[x for x in z.namelist() if x.startswith('CSV/') and not x.endswith('/')][0]
        hdr=pd.read_csv(z.open(n),sep='\t',nrows=0).columns
        ac='EDAD5' if 'EDAD5' in hdr else 'EDAD1'  # 2021+ names the 5-year band EDAD1
        d=pd.read_csv(z.open(n),sep='\t',dtype=str,usecols=['CICLO','NIVEL',ac,'RELPP1','SEXO1','NPADRE','NMADRE','FACTOREL']).rename(columns={ac:'EDAD5'})
        d['FACTOREL']=pd.to_numeric(d.FACTOREL.str.replace(',','.'),errors='coerce')
    return d
for y in yrs:
    fn=OUT+f'{y}.json'
    if os.path.exists(fn) or not os.path.exists(RAW+f'datos_2t{y%100:02d}.zip'): continue
    d=load(y)
    d=d[d.NIVEL.astype(str).str.strip()=='1']
    hh=d.FACTOREL[d.RELPP1.astype(str).str.strip()=='1'].sum()  # households = reference persons, weighted
    d=d[d.EDAD5.astype(str).str.strip().isin(['25','30'])].copy()
    d['rel3']=(d.RELPP1.astype(str).str.strip()=='3')
    d['parent']=d.rel3|nz(d.NPADRE)|nz(d.NMADRE)
    d['band']=d.EDAD5.astype(str).str.strip().map({'25':'25-29','30':'30-34'})
    res={'hh':hh,'year':y,'ciclos':d.CICLO.value_counts().to_dict(),'rows':[]}
    for gname,sub in [('25-29',d[d.band=='25-29']),('30-34',d[d.band=='30-34']),('25-34',d)]:
        for sx,s2 in [('T',sub),('M',sub[sub.SEXO1.astype(str).str.strip()=='1']),('F',sub[sub.SEXO1.astype(str).str.strip()=='6'])]:
            w=s2.FACTOREL.sum()
            res['rows'].append(dict(group=gname,sex=sx,n=len(s2),w=w,rel3=(s2.FACTOREL*s2.rel3).sum()/w*100,parent=(s2.FACTOREL*s2.parent).sum()/w*100))
    json.dump(res,open(fn,'w'));print(y,res['ciclos'],flush=True)
rows=[]
for y in range(1999,2026):
    fn=OUT+f'{y}.json'
    if not os.path.exists(fn): continue
    r=json.load(open(fn))
    if 'rows' not in r: continue
    for x in r['rows']:
        for var,key in [('share_living_with_parent_rel3','rel3'),('share_living_with_parent_any','parent')]:
            rows.append(dict(date=f'{y}-Q2',geo='ES',group=x['group']+('' if x['sex']=='T' else ' '+x['sex']),variable=var,value=round(x[key],2),unit='% of persons in age band',source_id='ine_epa_microdata_q2'))
    rows.append(dict(date=f'{y}-Q2',geo='ES',group='',variable='households_epa_microdata',value=round(r['hh'],0),unit='households',source_id='ine_epa_microdata_q2'))
pd.DataFrame(rows).to_csv('data/clean/c01_epa.csv',index=False)
print(len(rows),'rows')
