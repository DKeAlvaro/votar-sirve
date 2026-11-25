"""NL: share of persons living at home as 'thuiswonend kind' (child in parental household), by age band.
share = thuiswonend kind / total persons (incl. institutional households)."""
import requests,csv,json,os,re
R='data/raw/c01/';B='https://opendata.cbs.nl/ODataApi/odata/'
def get(url,fn):
    p=R+fn
    if not os.path.exists(p):
        out=[];u=url
        while u:
            j=requests.get(u,timeout=25).json();out+=j['value'];u=j.get('odata.nextLink')
        json.dump(out,open(p,'w'))
    return json.load(open(p))
rows=[]
def yr(p): return re.match(r'(\d{4})',p).group(1)
def fetch_old(t):
    f=f'cbs_{t}.json'
    d=get(B+t+"/TypedDataSet?$format=json",f)
    sex=[x for x in get(B+t+"/Geslacht?$format=json",f'cbs_{t}_sex.json')]
    age={x['Key']:x['Title'] for x in get(B+t+"/Leeftijd?$format=json",f'cbs_{t}_age.json')}
    tot=[x['Key'] for x in sex if x['Title'].strip().lower().startswith(('totaal','mannen en'))][0]
    for r in d:
        if r['Geslacht']!=tot: continue
        a=r['Leeftijd'].strip()
        g={'53500':'Y25-34','53050':'Y15-24'}.get(a)
        if not g or r['ThuiswonendKind_3'] is None: continue
        rows.append((yr(r['Perioden']),'NL',g,'share_living_with_parents',round(100*r['ThuiswonendKind_3']/r['TotaalPersonenInHuishoudens_1'],2),'percent','cbs_'+t))
for t in ['82986NED','81519NED']: fetch_old(t)
d=get(B+"37973/TypedDataSet?$format=json&$filter="+"Geslacht eq 'T001038' and Migratieachtergrond eq 'T001040' and Generatie eq 'T001040' and (Leeftijd eq '70400' or Leeftijd eq '70500' or Leeftijd eq '70600' or Leeftijd eq '70700')".replace(' ','%20'),'cbs_37973.json')
mg=[x for x in get(B+"37973/Migratieachtergrond?$format=json",'cbs_37973_mig.json') if x['Title'].startswith('Totaal')][0]['Key']
ge=[x for x in get(B+"37973/Generatie?$format=json",'cbs_37973_gen.json')]
sx=[x for x in get(B+"37973/Geslacht?$format=json",'cbs_37973_sex.json') if x['Title'].startswith('Totaal')][0]['Key']
ges=[x['Key'] for x in ge if x['Title'].startswith('Totaal')][0] if any(x['Title'].startswith('Totaal') for x in ge) else None
sub={}
for r in d:
    if r['Geslacht']!=sx or r['Migratieachtergrond']!=mg or (ges and r['Generatie']!=ges): continue
    sub.setdefault(yr(r['Perioden']),{})[r['Leeftijd']]=r
for y,m in sub.items():
    for g,keys in {'Y25-29':['70600'],'Y30-34':['70700'],'Y25-34':['70600','70700'],'Y15-24':['70400','70500']}.items():
        k=[m[x] for x in keys if x in m]
        if len(k)!=len(keys): continue
        th=sum(x['ThuiswonendKind_2'] for x in k);to=sum(x['TotaalAantalPersonenInHuishoudens_1'] for x in k)
        rows.append((y,'NL',g,'share_living_with_parents',round(100*th/to,2),'percent','cbs_37973'))
# 85378NED single years
f=R+'cbs_85378.json'
if not os.path.exists(f):
    u=B+"85378NED/TypedDataSet?$format=json&$filter=Geslacht eq 'T001038' and PositieInHuishouden eq 'T001105' and Herkomstland eq 'T001040' and Geboorteland eq 'T001638'".replace(' ','%20')
    u+=''
    get(u,'cbs_85378.json')
d=get('',f) if False else json.load(open(f))
ages=[x for x in json.load(open(R+'cbs_85378_age.json'))] if os.path.exists(R+'cbs_85378_age.json') else get(B+"85378NED/Leeftijd?$format=json",'cbs_85378_age.json')
th=get(B+"85378NED/TypedDataSet?$format=json&$filter=Geslacht eq 'T001038' and PositieInHuishouden eq '1016440' and Herkomstland eq 'T001040' and Geboorteland eq 'T001638'".replace(' ','%20'),'cbs_85378_kids.json')
title={x['Key']:x['Title'] for x in ages}
def band(k):
    m=re.match(r'(\d+) jaar$',title.get(k,''));
    return int(m.group(1)) if m else None
T={};H={}
for src,dst in((d,T),(th,H)):
    for r in src:
        a=band(r['Leeftijd'])
        if a is not None and 25<=a<=34 and r['Bevolking_1'] is not None: dst[(yr(r['Perioden']),a)]=r['Bevolking_1']
for y in sorted({k[0] for k in T}):
    if all((y,a) in T and (y,a) in H for a in range(25,35)):
        rows.append((y,'NL','Y25-34','share_living_with_parents',round(100*sum(H[(y,a)] for a in range(25,35))/sum(T[(y,a)] for a in range(25,35)),2),'percent','cbs_85378'))
rows.sort(key=lambda r:(r[6],r[2],r[0]))
with open('data/clean/c01_nl_cbs.csv','w',newline='') as o:
    w=csv.writer(o);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows))
