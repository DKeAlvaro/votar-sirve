"""c05/c06 job tenure by age (Eurostat LFS). Run: python -I scripts/c05_tenure.py"""
import sys,os,csv
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import _eurostat as E
G=[('geo','ES'),('geo','PT'),('geo','EU27_2020'),('geo','EU28'),('geo','EU15'),('sex','T')]
rows=[]
d=E.fetch('lfsa_egad',G+[('unit','PC')],'data/raw/c05/lfsa_egad.json')
for r in E.rows(d):
    if r['duration']=='TOTAL' or r['duration']=='NRP': continue
    rows.append([r['time'],r['geo'],r['age'].replace('Y','').replace('_GE','+'),'share_employed_tenure_'+r['duration'],r['value'],'percent_of_employed_in_age_group','eurostat_lfsa_egad'])
d=E.fetch('lfsa_egad',G+[('unit','THS_PER'),('duration','TOTAL')],'data/raw/c05/lfsa_egad_total.json')
for r in E.rows(d):
    rows.append([r['time'],r['geo'],r['age'].replace('Y','').replace('_GE','+'),'employed_total',r['value'],'thousand_persons','eurostat_lfsa_egad'])
rows.sort(key=lambda r:(r[3],r[1],r[2],r[0]))
with open('data/clean/c05_tenure_annual.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows))
# quarterly (c06)
rows=[]
Q=[('geo','ES'),('geo','PT'),('geo','EU27_2020'),('sex','T'),('nace_r2','TOTAL')]
d=E.fetch('lfsq_egdn2',Q+[('unit','THS_PER')],'data/raw/c06/lfsq_egdn2.json')
tot={}
for r in E.rows(d):
    tot[(r['time'],r['geo'],r['age'],r['duration'])]=r['value']
for (t,g,a,du),v in tot.items():
    if du=='M_LT3':
        T=tot.get((t,g,a,'TOTAL'))
        if T: rows.append([t,g,a.replace('Y','').replace('_GE','+'),'share_employed_tenure_lt3m',round(100*v/T,2),'percent_of_employed_in_age_group','eurostat_lfsq_egdn2 (derived from thousands)'])
rows.sort(key=lambda r:(r[1],r[2],r[0]))
with open('data/clean/c06_tenure_quarterly.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows))
