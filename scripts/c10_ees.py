"""c10: public vs private pay and contract stability in Spain from INE EES (Encuesta Cuatrienal de Estructura Salarial).
(a) published INE tables 36887 (2022) / 70728 (2018): mean gross annual wage by control (public/private), sex, CCAA.
(b) INE public microdata (https://www.ine.es/ftp/microdatos/salarial/datos_<year>.zip) -> cells education x age x control.
Run: python -I scripts/c10_ees.py   (microdata must be unzipped in data/raw/c10/ees_micro_<y>/x/)"""
import sys,os,json,csv,re
import numpy as np,pandas as pd
R='data/raw/c10/';O='data/clean/'
HDR='date,geo,group,variable,value,unit,source_id'.split(',')
# (a) published tables
CC={'Andaluc':'ES-AN','Arag':'ES-AR','Asturias':'ES-AS','Balears':'ES-IB','Canarias':'ES-CN','Cantabria':'ES-CB','Castilla y Le':'ES-CL','Castilla - La':'ES-CM','Catalu':'ES-CT','Comunitat Valenciana':'ES-VC','Extremadura':'ES-EX','Galicia':'ES-GA','Madrid':'ES-MD','Murcia':'ES-MC','Navarra':'ES-NC','Pa':'ES-PV','Rioja':'ES-RI','Ceuta':'ES-CE','Melilla':'ES-ML'}
rows=[]
for t in (70728,36887):
    d=json.load(open(R+'ine_ees_%d.json'%t,encoding='utf-8'))
    for x in d:
        p=x['Nombre'].split('. ')
        geo='ES' if p[0].startswith('Total Nacional') else next((v for k,v in CC.items() if p[0].startswith(k)),None)
        if geo is None: continue
        ctl={'Total':'all','Control de la empresa p\xfablico':'public','Control de la empresa privado':'private'}.get(p[2])
        sex={'Total':'all','Mujeres':'women','Hombres':'men'}[p[3]]
        if ctl is None: continue
        for y in x['Data']:
            if y['Valor'] is not None: rows.append([y['Anyo'],geo,'%s|%s'%(ctl,sex),'mean_gross_annual_wage',y['Valor'],'EUR_per_year_nominal','ine_eaes_%d'%t])
rows=sorted({tuple(r) for r in rows})
with open(O+'c10_ees_public_private_published.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(HDR);w.writerows(rows)
print('published',len(rows))
# (b) microdata
def wmedian(v,w):
    o=np.argsort(v);v=v[o];w=w[o];c=np.cumsum(w);return v[np.searchsorted(c,c[-1]/2)]
EDU={1:'less_than_primary',2:'primary',3:'lower_secondary',4:'upper_secondary',5:'vocational_higher',6:'university_diploma',7:'university_degree_phd'}
EDG={'low(<=lower_secondary)':[1,2,3],'mid(upper_secondary+vocational)':[4,5],'high(university)':[6,7],'all':list(EDU)}
AGE={'01':'<20','02':'20-29','03':'30-39','04':'40-49','05':'50-59','06':'60+'}
rows=[]
for y,f,sep in ((2018,'CSV/EES_2018.csv',','),(2022,'CSV/EES_2022.tab','\t')):
    d=pd.read_csv(R+'ees_micro_%d/x/%s'%(y,f),sep=None,engine='python',usecols=['CONTROL','ESTU','ANOS2','FACTOTAL','RETRINOIN','RETRIIN','GEXTRA','TIPOJOR','TIPOCON','DRELABAM','JAP','SEXO'],dtype={'ANOS2':str})
    d['pay']=d[['RETRINOIN','RETRIIN','GEXTRA']].sum(axis=1)
    d['ctl']=d.CONTROL.map({1:'public',2:'private'});d['age']=d.ANOS2.map(AGE)
    sid='ine_ees_micro_%d'%y
    # reconciliation vs published: mean over all workers
    for c in ('public','private'):
        s=d[d.ctl==c];rows.append([y,'ES','%s|all|all'%c,'check_mean_gross_annual_wage_all_workers',round(np.average(s.pay,weights=s.FACTOTAL),2),'EUR_per_year_nominal',sid])
    ft=d[(d.TIPOJOR==1)&(d.DRELABAM==12)&(d.JAP>0)].copy()
    ft['hourly']=ft.pay/ft.JAP
    for c in ('public','private'):
        for eg,codes in EDG.items():
            for ag in ['all']+list(AGE.values()):
                g='%s|%s|%s'%(c,eg,ag)
                a=d[(d.ctl==c)&d.ESTU.isin(codes)&((d.age==ag) if ag!='all' else True)]
                b=ft[(ft.ctl==c)&ft.ESTU.isin(codes)&((ft.age==ag) if ag!='all' else True)]
                if len(a)>=30:
                    rows.append([y,'ES',g,'share_permanent_contract',round(100*a.FACTOTAL[a.TIPOCON==1].sum()/a.FACTOTAL.sum(),2),'percent_of_employees',sid])
                    rows.append([y,'ES',g,'employees_weighted',round(a.FACTOTAL.sum()/1000,1),'thousand_employees',sid])
                    rows.append([y,'ES',g,'n_sample',len(a),'records',sid])
                if len(b)>=30:
                    rows.append([y,'ES',g,'mean_gross_annual_wage_ft_fullyear',round(np.average(b.pay,weights=b.FACTOTAL),2),'EUR_per_year_nominal',sid])
                    rows.append([y,'ES',g,'median_gross_annual_wage_ft_fullyear',round(wmedian(b.pay.values,b.FACTOTAL.values),2),'EUR_per_year_nominal',sid])
                    rows.append([y,'ES',g,'median_gross_hourly_wage_ft_fullyear',round(wmedian(b.hourly.values,b.FACTOTAL.values),3),'EUR_per_hour_nominal',sid])
with open(O+'c10_ees_public_private_micro.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(HDR);w.writerows(rows)
print('micro',len(rows))
