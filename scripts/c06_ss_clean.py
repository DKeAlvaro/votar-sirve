"""Clean Seguridad Social afiliados medios tables -> data/clean/c06_ss_*.csv. python -I scripts/c06_ss_clean.py"""
import sys,os,csv,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import _px
R='data/raw/c06/';O='data/clean/'
AGE=lambda s:{'Total Edad':'total','Mas de 64 a\xf1os':'65+'}.get(s) or re.sub(r'Entre (\d+) y (\d+) a\xf1os',r'\1-\2',s)
def ym(p): return p[:4]+'-'+p[4:]
def write(name,rows):
    with open(O+name,'w',newline='') as f:
        w=csv.writer(f);w.writerow('date,geo,group,variable,value,unit,source_id'.split(','));w.writerows(rows)
    print(name,len(rows),rows[0][:5],rows[-1][:5])
SLUG=lambda s:re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
# 01m age x regime (both sexes)
rows=[]
for d,v in _px.parse(R+'ss_01m_sexo_edad_regimen.px'):
    if d['Sexo']!='Total Sexo' or v is None: continue
    reg=d['Reg\xedmenes']
    if reg not in('Todos los Regimenes','REGIMEN GENERAL','REG. ESP. AUTONOMOS'): continue
    rows.append([ym(d['Periodo']),'ES',AGE(d['Tramos de edad']),'affiliates_avg_'+SLUG(reg),v,'persons','ss_pxweb_01m'])
write('c06_ss_affiliation_age_regime.csv',rows)
# 07m RG x contract type x age
rows=[]
for d,v in _px.parse(R+'ss_07m_rg_contrato_jornada_edad_sexo.px'):
    if d['Sexo']!='Total Sexo' or v is None: continue
    rows.append([ym(d['Periodo']),'ES',AGE(d['Tramos de edad']),'affiliates_rg_'+SLUG(d['tipo contrato']),v,'persons','ss_pxweb_07m'])
write('c06_ss_rg_contract_age.csv',rows)
# 11m province x age
rows=[];names={}
for d,v in _px.parse(R+'ss_11m_provincia_edad_sexo.px'):
    if d['Sexo']!='Total Sexo' or v is None: continue
    p=d['Provincia']
    if p=='Total Nacional': geo='ES'
    else:
        n,name=p.split('. ',1);geo='ES-%02d'%int(n);names[geo]=name
    rows.append([ym(d['Periodo']),geo,AGE(d['Tramos de edad']),'affiliates_avg_all_regimes',v,'persons','ss_pxweb_11m'])
write('c06_ss_province_age.csv',rows)
with open(O+'c06_province_names.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['geo','name']);[w.writerow([k,v]) for k,v in sorted(names.items())]
