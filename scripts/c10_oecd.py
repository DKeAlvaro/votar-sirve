"""c10: general government employment as % of total employment, OECD Government at a Glance (yearly updates flow).
Run: python -I scripts/c10_oecd.py"""
import requests,os,csv
R='data/raw/c10/oecd_DF_GOV_EMPPS_REP_YU.csv';O='data/clean/c10_oecd_gov_employment.csv'
if not os.path.exists(R):
    r=requests.get('https://sdmx.oecd.org/public/rest/data/OECD.GOV.GIP,DSD_GOV@DF_GOV_EMPPS_REP_YU,/all?dimensionAtObservation=AllDimensions',headers={'Accept':'application/vnd.sdmx.data+csv; charset=utf-8'},timeout=28)
    r.raise_for_status();open(R,'w',encoding='utf-8').write(r.text)
rows=[]
for d in csv.DictReader(open(R,encoding='utf-8')):
    if d['MEASURE']!='EMPG' or d['UNIT_MEASURE']!='PT_EMP' or d['SECTOR']!='S13' or not d['OBS_VALUE']: continue
    g='OECD_AVG' if d['REF_AREA']=='OECD_REP' else d['REF_AREA']
    rows.append([d['TIME_PERIOD'],g,'','general_government_employment_pct_of_total_employment',float(d['OBS_VALUE']),'percent','oecd_gaag_DF_GOV_EMPPS_REP_YU'])
rows.sort(key=lambda r:(r[1],r[0]))
with open(O,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows))
