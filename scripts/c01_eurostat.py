import json,csv,os,sys,urllib.request
R='data/raw/c01/';O='data/clean/c01_eurostat.csv'
base='https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/%s?format=JSON&lang=en'
for c in ['ilc_lvps08','yth_demo_030']:
    if not os.path.exists(R+c+'.json'): urllib.request.urlretrieve(base%c,R+c+'.json')
rows=[]
def go(c,geos,var,unit,sid,sexes=('T',),ages=None):
    d=json.load(open(R+c+'.json'));ids=d['id'];dim=d['dimension']
    idx={k:list(dim[k]['category']['index']) for k in ids};sz=d['size']
    for flat,v in d['value'].items():
        f=int(flat);pos={}
        for k in reversed(ids):
            n=len(idx[k]);pos[k]=idx[k][f%n];f//=n
        if pos['geo'] not in geos or pos['sex'] not in sexes: continue
        if ages and pos.get('age') not in ages: continue
        rows.append([pos['time'],pos['geo'],pos.get('age','') ,var,v,unit,sid])
go('ilc_lvps08',('ES','NL','EU27_2020','EU28','EU'),'share_living_with_parents','percent','eurostat_ilc_lvps08')
go('yth_demo_030',('ES','NL','EU27_2020'),'avg_age_leaving_parental_home','years','eurostat_yth_demo_030')
# sex goes into group for clarity
rows.sort(key=lambda r:(r[3],r[1],r[2],r[0]))
with open(O,'w',newline='') as f:
    w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
print(len(rows))
