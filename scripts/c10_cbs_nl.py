"""c10 NL: CBS 81431ned employee jobs by industry (O public administration, P education, Q health) vs all. python -I scripts/c10_cbs_nl.py"""
import requests,json,os,csv,urllib.parse
R='data/raw/c10/cbs_81431ned.json';O='data/clean/c10_nl_cbs_jobs_by_industry.csv'
B='https://opendata.cbs.nl/ODataApi/odata/81431ned/TypedDataSet'
if not os.path.exists(R):
    f="KenmerkenBaanWerknemerBedrijf eq 'T001098' and (BedrijfstakkenBranchesSBI2008 eq 'T001081' or BedrijfstakkenBranchesSBI2008 eq '417400 ' or BedrijfstakkenBranchesSBI2008 eq '419000 ' or BedrijfstakkenBranchesSBI2008 eq '422400 ')"
    r=requests.get(B,params={'$format':'json','$filter':f},timeout=25);r.raise_for_status();open(R,'w',encoding='utf-8').write(r.text)
d=json.load(open(R,encoding='utf-8'))['value']
S={'T001081':'all','417400':'O_public_administration','419000':'P_education','422400':'Q_health_social'}
rows=[];by={}
for x in d:
    s=S[x['BedrijfstakkenBranchesSBI2008'].strip()];y=x['Perioden'][:4]
    by[(y,s)]=x
    for k,v,u in [('Banen_1','jobs','thousand_jobs'),('JaarloonInclusiefBijzondereBeloning_6','annual_wage_incl_bonus','EUR_per_year_nominal'),('Uurloon_3','hourly_wage','EUR_per_hour_nominal')]:
        if x.get(k) is not None: rows.append([y,'NL',s,v,x[k],u,'cbs_81431ned'])
for y in sorted({k[0] for k in by}):
    a=by[(y,'all')]['Banen_1']
    for s in ['O_public_administration','P_education','Q_health_social']:
        rows.append([y,'NL',s,'share_of_employee_jobs',round(100*by[(y,s)]['Banen_1']/a,2),'percent','derived_cbs_81431ned'])
    t=sum(by[(y,s)]['Banen_1'] for s in ['O_public_administration','P_education','Q_health_social'])
    rows.append([y,'NL','O+P+Q','share_of_employee_jobs',round(100*t/a,2),'percent','derived_cbs_81431ned'])
with open(O,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows))
