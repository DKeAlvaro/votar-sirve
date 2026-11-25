"""c05 youth unemployment: INE EPA (1976-) + Eurostat controls. Run: python -I scripts/c05_unemployment.py"""
import sys,os,re,csv,datetime
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__))))
import _ine,_eurostat as E
R='data/raw/c05/';O='data/clean/'
rows=[]
# --- INE pre-2002 PC-Axis
SEXES=None
def parse_px(f):
    t=open(f,encoding='latin-1').read()
    def vals(name):
        m=re.search(r'VALUES\("%s"\)=(.*?);'%re.escape(name),t,re.S)
        return re.findall(r'"([^"]*)"',m.group(1))
    stub=re.search(r'STUB=(.*?);',t,re.S).group(1);stub=re.findall(r'"([^"]*)"',stub)
    head=re.search(r'HEADING=(.*?);',t,re.S).group(1);head=re.findall(r'"([^"]*)"',head)
    data=re.search(r'DATA=(.*?);',t,re.S).group(1).split()
    S=[vals(s) for s in stub];H=[vals(h) for h in head]
    import itertools
    rws=list(itertools.product(*S));cols=list(itertools.product(*H))
    assert len(data)==len(rws)*len(cols),(len(data),len(rws),len(cols))
    k=0
    for r in rws:
        for c in cols:
            yield dict(zip(stub,r))|dict(zip(head,c)),data[k];k+=1
AGE={'menores de 25 a\xf1os':'16-24','de 25 y m\xe1s a\xf1os':'25+','de 16 a 19 a\xf1os':'16-19','de 20 a 24 a\xf1os':'20-24','de 25 a 54 a\xf1os':'25-54','de 55 y m\xe1s a\xf1os':'55+','total':'16+'}
for f,sid in [('ine_epa_1976_1995_01011.px','ine_epa_px_1976_1995'),('ine_epa_1996_2001_01011.px','ine_epa_px_1996_2001')]:
    for d,v in parse_px(R+f):
        if d['Tipo de tasa']!='tasas de paro' or d['Sexo']!='ambos sexos': continue
        m=re.match(r'(\d{4})T(I+|IV)$',d['Periodo']);q={'I':1,'II':2,'III':3,'IV':4}[m.group(2)]
        if v in ('.','..','-'): continue
        rows.append(['%s-Q%d'%(m.group(1),q),'ES',AGE[d['Distintos grupos de edad']],'unemployment_rate',float(v),'percent',sid])
# --- INE API 2002-
API={'EPA423474':'16+','EPA452436':'16-24','EPA423476':'16-19','EPA423477':'20-24','EPA423478':'25-29','EPA452438':'25-54','EPA452439':'55+','EPA423479':'30-34'}
for cod,g in API.items():
    d=_ine.get('DATOS_SERIE/%s?nult=600'%cod,R+'ine_api_%s.json'%cod)
    for x in d['Data']:
        dt=datetime.datetime.fromtimestamp(x['Fecha']/1000)
        q=(dt.month-1)//3+1
        rows.append(['%d-Q%d'%(dt.year,q),'ES',g,'unemployment_rate',x['Valor'],'percent','ine_epa_api_2002_'+cod])
# derived 25+ not available post-2002 except via bands; skip
# --- Eurostat
for code,par,sid in [('une_rt_a',[('geo','ES'),('geo','PT'),('geo','EU27_2020'),('sex','T'),('unit','PC_ACT')],'eurostat_une_rt_a'),
                     ('une_rt_q',[('geo','ES'),('geo','PT'),('geo','EU27_2020'),('sex','T'),('unit','PC_ACT'),('s_adj','NSA')],'eurostat_une_rt_q'),
                     ('lfsa_urgan',[('geo','ES'),('geo','PT'),('geo','EU27_2020'),('sex','T'),('unit','PC'),('citizen','TOTAL')],'eurostat_lfsa_urgan')]:
    d=E.fetch(code,par,R+code+'.json')
    for r in E.rows(d):
        if r['age'] not in ('Y15-19','Y20-24','Y25-29','Y15-24','Y15-29','Y25-54','Y25-74','Y15-74','Y20-64'): continue
        rows.append([r['time'],r['geo'],r['age'].replace('Y','').replace('_GE','+'),'unemployment_rate',r['value'],'percent',sid])
# derived annual mean of the 4 quarters (simple average of quarterly rates)
from collections import defaultdict
acc=defaultdict(list)
for r in list(rows):
    if '-Q' in r[0] and r[6].startswith('ine_'): acc[(r[0][:4],r[2],r[6])].append(r[4])
for (y,g,s),v in acc.items():
    if len(v)==4: rows.append([y,'ES',g,'unemployment_rate',round(sum(v)/4,2),'percent','derived_annual_mean_of_'+s])
for f,sel in [('c05_unemployment_quarterly.csv',lambda r:'-Q' in r[0]),('c05_unemployment_annual.csv',lambda r:'-Q' not in r[0])]:
    rr=sorted([r for r in rows if sel(r)],key=lambda r:(r[6],r[1],r[2],r[0]))
    with open(O+f,'w',newline='') as fh:
        w=csv.writer(fh);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rr)
    print(f,len(rr))
