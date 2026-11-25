"""Eurostat business demography (bd_9bd_sz_cl_r2, bd_9pm_r2). Rerunnable; raw -> data/raw/c08."""
import json,csv,os,urllib.request
R='data/raw/c08/';B='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'
U={'bd_sz.json':B+'bd_9bd_sz_cl_r2?format=JSON&geo=ES&geo=NL&geo=EU27_2020&sizeclas=TOTAL&nace_r2=B-S_X_K642&lang=EN',
   'bd_hg.json':B+'bd_9pm_r2?format=JSON&geo=ES&geo=NL&geo=EU27_2020&nace_r2=B-N_X_K642&indic_sb=V97460&lang=EN'}
for f,u in U.items():
    if not os.path.exists(R+f): urllib.request.urlretrieve(u,R+f)
def rd(f,sid,keep):
    d=json.load(open(R+f));ids=d['id'];idx={k:list(d['dimension'][k]['category']['index']) for k in ids}
    out=[]
    for flat,v in d['value'].items():
        f_=int(flat);pos={}
        for k in reversed(ids):
            n=len(idx[k]);pos[k]=idx[k][f_%n];f_//=n
        if pos['indic_sb'] in keep: out.append([pos['time'],pos['geo'],'',keep[pos['indic_sb']][0],v,keep[pos['indic_sb']][1],sid])
    return out
keep={'V97020':('enterprise_birth_rate','percent of active enterprises'),'V97030':('enterprise_death_rate','percent of active enterprises'),
 'V97041':('survival_rate_1y','percent of births (t-1 cohort)'),'V97043':('survival_rate_3y','percent of births (t-3 cohort)'),'V97045':('survival_rate_5y','percent of births (t-5 cohort)'),
 'V97253':('cohort_survival_3y','percent of births in n'),'V97255':('cohort_survival_5y','percent of births in n'),'V11910':('active_enterprises','number'),'V11920':('enterprise_births','number')}
rows=rd('bd_sz.json','eurostat_bd_9bd_sz_cl_r2',keep)
rows+=rd('bd_hg.json','eurostat_bd_9pm_r2',{'V97460':('high_growth_share_10plus_emp','percent of enterprises with >=10 employees')})
rows.sort(key=lambda r:(r[3],r[1],r[0]))
with open('data/clean/c08_eurostat_bd.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
for r in rows:
    if r[1] in('ES','NL') and r[3] in('enterprise_birth_rate','survival_rate_5y','high_growth_share_10plus_emp') and r[0] in ('2008','2019','2020','2021','2022'): print(r)
print(len(rows))
