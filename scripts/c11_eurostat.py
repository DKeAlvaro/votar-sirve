"""c11: Eurostat health tables -> clean CSVs. Run: python -I scripts/c11_eurostat.py (from repo root)."""
import json,csv,os,sys,urllib.request
R='data/raw/c11/';OUT='data/clean/'
B='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/%s?format=JSON&lang=en%s'
SILC='&sex=T&quant_inc=TOTAL&reason=TXP&reason=WLIST&reason=TFAR&reason=TXP_TFAR_WLIST'
for code,q in [('hlth_sha11_hf',''),('demo_mlexpec',''),('hlth_cd_apr',''),('hlth_silc_08',SILC),('hlth_silc_08b','')]:
    p=R+code+'.json'
    if not os.path.exists(p): urllib.request.urlretrieve(B%(code,q),p)
GEOS={'AT','BE','BG','CY','CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK','NO','CH','IS','UK','EU27_2020'}
def cells(code):
    d=json.load(open(R+code+'.json'));ids=d['id'];idx={k:list(d['dimension'][k]['category']['index']) for k in ids}
    for flat,v in d['value'].items():
        f=int(flat);pos={}
        for k in reversed(ids):
            n=len(idx[k]);pos[k]=idx[k][f%n];f//=n
        if pos['geo'] in GEOS: yield pos,v
rows=[]
def add(pos,var,v,unit,sid,group=''): rows.append([pos['time'],pos['geo'],group,var,v,unit,sid])
# health expenditure
for pos,v in cells('hlth_sha11_hf'):
    u,h=pos['unit'],pos['icha11_hf']
    s='eurostat_hlth_sha11_hf'
    if h=='TOT_HF' and u=='PPS_HAB': add(pos,'health_exp_per_capita_pps',v,'PPS per inhabitant',s)
    elif h=='TOT_HF' and u=='EUR_HAB': add(pos,'health_exp_per_capita_eur',v,'EUR per inhabitant (nominal)',s)
    elif h=='TOT_HF' and u=='PC_GDP': add(pos,'health_exp_pct_gdp',v,'% of GDP',s)
    elif h=='HF3' and u=='PPS_HAB': add(pos,'oop_per_capita_pps',v,'PPS per inhabitant',s)
    elif h=='HF3' and u=='PC_CHE': add(pos,'oop_share_of_health_exp',v,'% of current health expenditure',s)
    elif h=='HF1' and u=='PC_CHE': add(pos,'govt_compulsory_share_of_health_exp',v,'% of current health expenditure',s)
write=lambda name,rs:(lambda f:(lambda w:(w.writerow('date,geo,group,variable,value,unit,source_id'.split(',')),w.writerows(sorted(rs,key=lambda r:(r[3],r[1],r[2],r[0])))))(csv.writer(f)))(open(OUT+name,'w',newline='')) 
write('c11_health_expenditure.csv',rows);print('exp',len(rows));rows=[]
# life expectancy at birth and at 65
for pos,v in cells('demo_mlexpec'):
    if pos['age'] in('Y_LT1','Y65'):
        add(pos,'life_expectancy_at_birth' if pos['age']=='Y_LT1' else 'life_expectancy_at_65',v,'years','eurostat_demo_mlexpec',{'T':'total','M':'male','F':'female'}[pos['sex']])
write('c11_life_expectancy.csv',rows);print('le',len(rows));rows=[]
# avoidable mortality (age-standardised rate per 100,000), all causes within category
for pos,v in cells('hlth_cd_apr'):
    if pos['icd10']=='TOTAL' and pos['unit']=='RT':
        var={'TRT':'treatable_mortality_rate','PRVT':'preventable_mortality_rate','TOTAL':'all_cause_mortality_rate'}[pos['mortalit']]
        add(pos,var,v,'deaths per 100,000 (standardised)','eurostat_hlth_cd_apr',{'T':'total','M':'male','F':'female'}[pos['sex']])
write('c11_avoidable_mortality.csv',rows);print('mort',len(rows));rows=[]
# unmet needs medical examination
for pos,v in cells('hlth_silc_08'):
    add(pos,'unmet_medical_'+pos['reason'].lower(),v,'% of people',  'eurostat_hlth_silc_08',pos['age'])
for pos,v in cells('hlth_silc_08b'):
    if pos['sex']=='T': add(pos,'unmet_medical_txp_tfar_wlist_by_poverty_'+pos['rskpovth'].lower(),v,'% of people','eurostat_hlth_silc_08b',pos['age'])
write('c11_unmet_needs.csv',rows);print('unmet',len(rows))
