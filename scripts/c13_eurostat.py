"""c13: Eurostat COFOG (gov_10a_exp) and population by age (demo_pjan), ES and NL. Run from repo root."""
import json,csv,os,re,urllib.request
R='data/raw/c13/';O='data/clean/'
E='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'
C=['TOTAL','GF07','GF09','GF10','GF1001','GF1002','GF1003','GF1004','GF1005','GF1006','GF1007','GF1008','GF1009']
Q={'gov_10a_exp':'?format=JSON&lang=en&geo=ES&geo=NL&sector=S13&na_item=TE'+''.join('&cofog99='+c for c in C),
   'demo_pjan':'?format=JSON&lang=en&geo=ES&geo=NL&sex=T'}
for c,q in Q.items():
    if not os.path.exists(R+c+'.json'): urllib.request.urlretrieve(E+c+q,R+c+'.json')
def cells(code):
    d=json.load(open(R+code+'.json'));ids=d['id'];idx={k:list(d['dimension'][k]['category']['index']) for k in ids}
    for flat,v in d['value'].items():
        f=int(flat);pos={}
        for k in reversed(ids):
            n=len(idx[k]);pos[k]=idx[k][f%n];f//=n
        yield pos,v
HDR='date,geo,group,variable,value,unit,source_id'.split(',')
def write(name,rows):
    rows.sort(key=lambda r:(r[3],r[1],r[2],r[0]))
    with open(O+name,'w',newline='') as f: w=csv.writer(f);w.writerow(HDR);w.writerows(rows)
    print(name,len(rows))
UN={'MIO_EUR':('cofog_expenditure_eur_m','EUR million (nominal)'),'MIO_NAC':('cofog_expenditure_nac_m','national currency million (nominal; ES=EUR, NL=EUR)'),
    'PC_GDP':('cofog_expenditure_pct_gdp','% of GDP'),'PC_TOT':('cofog_expenditure_pct_total_exp','% of total general government expenditure')}
rows=[[p['time'],p['geo'],p['cofog99'],UN[p['unit']][0],v,UN[p['unit']][1],'eurostat_gov_10a_exp'] for p,v in cells('gov_10a_exp')]
write('c13_cofog.csv',rows)
pop={}
for p,v in cells('demo_pjan'):
    a=p['age']
    if a=='TOTAL': age='total'
    elif a=='Y_LT1': age=0
    elif a=='Y_OPEN': age=100
    elif re.fullmatch(r'Y\d+',a): age=int(a[1:])
    else: continue
    pop[(p['time'],p['geo'],age)]=v
rows=[];rows2=[]
bands={'0-17':(0,17),'18-29':(18,29),'30-44':(30,44),'45-64':(45,64),'65+':(65,200),'0-29':(0,29),'20-34':(20,34),'18+':(18,200)}
for (t,g,a),v in pop.items():
    if a=='total': rows.append([t,g,'total','population',v,'persons (1 Jan)','eurostat_demo_pjan'])
    else: rows2.append([t,g,'Y%d'%a,'population',v,'persons (1 Jan)','eurostat_demo_pjan'])
for (t,g) in sorted({(k[0],k[1]) for k in pop}):
    for b,(lo,hi) in bands.items():
        ages=[a for a in range(lo,min(hi,100)+1) if (t,g,a) in pop]
        if len(ages)==min(hi,100)-lo+1: rows.append([t,g,b,'population',sum(pop[(t,g,a)] for a in ages),'persons (1 Jan)','eurostat_demo_pjan'])
write('c13_population_age_bands.csv',rows);write('c13_population_single_age.csv',rows2)
