"""c13: self-reported turnout by age band at each Spanish general election 1982-2023, from CIS post-electoral
microdata already downloaded by scripts/c13_cis_download.py (data/raw/c13/cis/<study>/x/).
Output: data/clean/c13_turnout_age.csv. Run from repo root: python -I scripts/c13_turnout_age.py
Rules (see sources/c13.md): voted = codes below; not voted = all other valid codes (incl. 'went but could not vote',
'could not vote'); excluded = no age to vote / no right to vote / doesn't remember / N.C.; age < 18 never present.
Weighted by PESO where the study has one (otherwise unweighted)."""
import re,csv,os,sys
import pandas as pd,numpy as np,pyreadstat
C='data/raw/c13/cis/%s/x/'
# study -> (date, kind, participation var, voted codes, not-voted codes, age var, weight var)
# for 2019 the participation question is only asked to abstainers, so participation is derived from vote recall
# (any vote/blank/null = voted, 'No votó' = not voted).
NV=lambda *a:set(a)
S=[('1982',1327,'sav','P1',NV(1),NV(2),'P26',None),
   ('1986',1542,'sav','P10',NV(1),NV(2,3,4),'P35','PESO'),
   ('1989',1842,'sav','P10',NV(1),NV(2,3,4),'P37','PESO'),
   ('1993',2061,'fw','P10',NV(1),NV(2,3,4),'P37',None),
   ('1996',2210,'sav','P8',NV(1),NV(2,3,4),'P44','PESO'),
   ('2000',2384,'fw','P32',NV(1),NV(2,3,4),'EDAD',None),
   ('2004',2559,'fw','P7',NV(1),NV(2,3,4),'P26','PESO'),
   ('2008',2757,'sav','p32',NV(4),NV(1,2,3),'edad','PESO'),
   ('2011',2920,'sav','p53',NV(1),NV(3,4,5),'EDAD','PESO'),
   ('2015',3126,'fw','P29',NV(5),NV(1,2,3,4),'EDAD','PESO'),
   ('2016',3145,'sav','P29',NV(5),NV(1,2,3,4),'P48',None),
   ('2019-04',3248,'sav','P23',None,NV(97),'P42',None),
   ('2019-11',3269,'sav','B22',None,NV(97),'C10','PESO'),
   ('2023',3420,'sav','PARTICIPACIONG1',NV(1,7),NV(2),'EDAD','PESO')]
def fw_layout(n,names):
    t=open(C%n+'ES%d'%n,encoding='latin1').read(); h=t[:t.find('\n\n')]
    h=h.split('.\n')[0] if n!=2559 else h
    out={}
    recs=re.split(r'\n/(?=[A-Z])',h)  # records
    for ri,rec in enumerate(recs):
        for m in re.finditer(r'\b([A-Za-z0-9_]+) (\d+)(?:-(\d+))?(?:\((\d)\))?(?=[\s.]|$)',rec):
            nm=m.group(1).upper()
            if nm in names: out[nm]=(ri-1,int(m.group(2))-1,int(m.group(3) or m.group(2)),m.group(4))
    return out
def read_fw(n,var,age,w):
    names={var.upper(),age.upper()}|({w} if w else set())
    if n==2559: L={'P7':(0,59,60,None),'P26':(0,137,139,None),'PESO':(0,204,210,'4')}
    else: L=fw_layout(n,names)
    nrec=3 if n==2061 else 1
    lines=open(C%n+'DA%d'%n,encoding='latin1').read().split('\n')
    lines=[l.rstrip('\r') for l in lines if l.strip()]
    rows=[]
    for i in range(0,len(lines),nrec):
        rec=lines[i:i+nrec]; d={}
        for nm,(ri,a,b,dec) in L.items():
            s=rec[ri][a:b].strip().replace(',','.') if ri<len(rec) else ''
            try: d[nm]=float(s)
            except: d[nm]=np.nan
        rows.append(d)
    df=pd.DataFrame(rows); return df,L
BANDS=[('18-24',18,24),('25-29',25,29),('30-34',30,34),('35-44',35,44),('45-54',45,54),('55-64',55,64),('65-74',65,74),('75+',75,200),
       ('18-29',18,29),('30-44',30,44),('45-64',45,64),('65+',65,200),('18+',18,200)]
rows=[];log=[]
for date,n,kind,var,vc,nvc,age,w in S:
    if kind=='sav':
        cols=[var,age]+([w] if w else [])
        df,meta=pyreadstat.read_sav(C%n+'%d.sav'%n,usecols=cols,encoding='latin1')
    else:
        df,L=read_fw(n,var,age,w); df=df.rename(columns={var.upper():var,age.upper():age})
    a=df[age]; a=a.where((a>=18)&(a<=97))
    x=df[var]
    if vc is None: voted=x.notna()&~x.isin([97,98,99,0])&(x>0)
    else: voted=x.isin(vc)
    valid=voted|x.isin(nvc)
    wt=df[w].fillna(1.0) if w else pd.Series(1.0,index=df.index)
    ok=valid&a.notna()
    for b,lo,hi in BANDS:
        m=ok&(a>=lo)&(a<=hi)
        nn=int(m.sum())
        if nn==0: continue
        pu=100*voted[m].mean()
        rows.append([date,'ES',b,'self_reported_turnout_pct_unweighted',round(pu,2),'% of valid answers','cis_%d'%n])
        if w: rows.append([date,'ES',b,'self_reported_turnout_pct_weighted',round(100*(wt[m]*voted[m]).sum()/wt[m].sum(),2),'% of valid answers','cis_%d'%n])
        rows.append([date,'ES',b,'n_valid',nn,'respondents (unweighted)','cis_%d'%n])
    log.append((date,n,len(df),int(valid.sum()),int(ok.sum()),round(100*voted[ok].mean(),1)))
OFF={'1982':79.97,'1986':70.49,'1989':69.74,'1993':76.44,'1996':77.38,'2000':68.71,'2004':75.66,'2008':73.85,'2011':68.94,
     '2015':73.20,'2016':66.48,'2019-04':71.76,'2019-11':66.23,'2023':70.40}
if os.path.exists('data/clean/c13_turnout_official.csv'):
    for r in csv.DictReader(open('data/clean/c13_turnout_official.csv')):
        if r['date']>='1982': rows.append([r['date'],'ES','all',r['variable'],float(r['value']),r['unit'],r['source_id']])
else: sys.exit('run c13_turnout_official.py first')
rows.sort(key=lambda r:(r[0],r[3],r[2]))
with open('data/clean/c13_turnout_age.csv','w',newline='') as f:
    wr=csv.writer(f);wr.writerow('date,geo,group,variable,value,unit,source_id'.split(','));wr.writerows(rows)
for l in log: print(*l)
