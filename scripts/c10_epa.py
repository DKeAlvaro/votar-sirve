"""c10: public employment share and public vs private temporary rate, INE EPA. Run: python -I scripts/c10_epa.py
Uses raw tables already in data/raw/c10 (65187/65189 asalariados by age, 65195/65196 by contract, 65198/65199 contract x age) + series EPA387796 (ocupados)."""
import sys,os,json,csv,datetime,re,statistics
from collections import defaultdict
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import _ine
R='data/raw/c10/';O='data/clean/'
def load(f): return json.load(open(R+f,encoding='utf-8'))
def q(ms):
    dt=datetime.datetime.fromtimestamp(ms/1000+6*3600,datetime.timezone.utc)
    return '%d-Q%d'%(dt.year,(dt.month-1)//3+1)
class _A(dict):
    def __contains__(self,k): return k=='Total' or bool(re.match(r'De \d+ a \d+ a.os$|70 y m.s a.os$',k))
    def __getitem__(self,k):
        if k=='Total': return '16+'
        m=re.match(r'De (\d+) a (\d+)',k);return '%s-%s'%m.groups() if m else '70+'
AGE=_A()
def series(f,sector):
    """yield (quarter, age, contract_or_None, value thousand) for Ambos sexos, valor absoluto"""
    for x in load(f):
        n=x['Nombre']
        if 'Valor absoluto' not in n or '. Ambos sexos. ' not in n: continue
        p=n.split('. Ambos sexos. ',1)[1].rsplit('. Valor absoluto',1)[0].split('. ')
        yield p,x
w=lambda rows,name:(lambda f:(lambda wr:(wr.writerow('date,geo,group,variable,value,unit,source_id'.split(',')),wr.writerows(rows)))(csv.writer(f)))(open(O+name,'w',newline='',encoding='utf-8'))
# ---- 1. public share of employment, ES quarterly
tot={}
for x in _ine.get('DATOS_SERIE/EPA387796?nult=200',R+'ine_EPA387796_ocupados.json')['Data']: tot[q(x['Fecha'])]=x['Valor']
pub={};asal={};priv={}
for tab,dst in [('ine_65189.json',pub),('ine_65187.json',asal),('ine_65188.json',priv)]:
    for p,x in series(tab,None):
        if len(p)==1 and p[0]=='Total' or (len(p)==2 and p[0]=='Total' and False):
            for y in x['Data']: dst[q(y['Fecha'])]=y['Valor']
# the "Total" entry of each table is Ambos sexos. Total
rows=[]
for d in sorted(tot):
    if d in pub and d in asal and d in priv:
        rows+= [[d,'ES','','employed_total',tot[d],'thousand_persons','ine_epa_EPA387796'],
                [d,'ES','','employees_total',asal[d],'thousand_persons','ine_epa_65187'],
                [d,'ES','','employees_public',pub[d],'thousand_persons','ine_epa_65189'],
                [d,'ES','','employees_private',priv[d],'thousand_persons','ine_epa_65188'],
                [d,'ES','','public_employees_pct_of_employed',round(100*pub[d]/tot[d],2),'percent','derived_ine_epa'],
                [d,'ES','','public_employees_pct_of_employees',round(100*pub[d]/asal[d],2),'percent','derived_ine_epa']]
# annual means
acc=defaultdict(list)
for r in rows:
    if r[3].startswith('public_employees_pct'): acc[(r[0][:4],r[3])].append(r[4])
for (y,v),l in sorted(acc.items()):
    if len(l)==4: rows.append([y,'ES','',v,round(sum(l)/4,2),'percent','derived_annual_mean_ine_epa'])
# by age: public share of employees
pa={};aa={}
for tab,dst in [('ine_65189.json',pa),('ine_65187.json',aa)]:
    for p,x in series(tab,None):
        if len(p)==1 and p[0] in AGE and p[0]!='Total':
            for y in x['Data']:
                if y['Valor'] is not None: dst[(q(y['Fecha']),AGE[p[0]])]=y['Valor']
for k in sorted(pa):
    if k in aa and aa[k]: rows.append([k[0],'ES',k[1],'public_employees_pct_of_employees',round(100*pa[k]/aa[k],2),'percent','derived_ine_epa_65189_65187'])
# by administration, annual 2006-2023
for cod,lab in [('EPA129599','total'),('EPA129598','central'),('EPA129597','social_security'),('EPA129596','autonomous_community'),('EPA129595','local'),('EPA129594','public_company_institution'),('EPA129593','other'),('EPA129592','unknown')]:
    for x in _ine.get('DATOS_SERIE/%s?nult=40'%cod,R+'ine_%s.json'%cod)['Data']:
        rows.append([str(x['Anyo']),'ES','','public_employees_'+lab,x['Valor'],'thousand_persons','ine_epa_4861_%s'%cod])
w(rows,'c10_public_employment_es.csv');print('c10_public_employment_es',len(rows))
# ---- 2. temporary rate public vs private by age and total
def contract(tab,sector,withage):
    out={}
    for p,x in series(tab,None):
        if withage:
            age=p[0];con='. '.join(p[1:])
            if age not in AGE: continue
            age=AGE[age]
            if age=='16+': continue
        else:
            age='16+';con='. '.join(p)
        if con not in('Total','Temporal: Total','De duraciÃ³n indefinida: Total'): continue
        for y in x['Data']:
            if y['Valor'] is not None: out[(q(y['Fecha']),age,con)]=y['Valor']
    return out
rows=[]
for sector,tab,withage in [('public','ine_65196.json',False),('private','ine_65195.json',False),('public','ine_65199.json',True),('private','ine_65198.json',True)]:
    o=contract(tab,sector,withage)
    for d in {k[0] for k in o}:
        for c in ('Total','Temporal: Total'):
            ks=[(d,a,c) for a in ('16-19','20-24','25-29')]
            if withage and all(k in o for k in ks): o[(d,'16-29',c)]=sum(o[k] for k in ks)
    for (d,a,c),v in sorted(o.items()):
        if c=='Temporal: Total':
            T=o.get((d,a,'Total'))
            if T: rows.append([d,'ES',a,'temporary_rate_'+sector,round(100*v/T,2),'percent_of_employees','derived_ine_epa_'+tab[4:9]])
rows=sorted({tuple(r) for r in rows},key=lambda r:(r[3],r[2],r[0]))
w(rows,'c10_temporary_rate_sector_es.csv');print('c10_temporary_rate_sector_es',len(rows))
